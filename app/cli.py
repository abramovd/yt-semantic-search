import json
import typer
import logging
from pathlib import Path
from app.services.video_processing import get_default_video_processing_service
from app.services.search import get_default_video_search_service
from app.services.crud import get_default_video_crud
from app.storage.models import SearchResultChunk
from app.logs import setup_rich_logging
from app.youtube.data_loader import Video

from rich.table import Table
from rich.console import Console

console = Console()


def global_callback(
    log_level: str = typer.Option(
        "INFO", 
        help="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    ),
):
    setup_rich_logging(level=logging._nameToLevel[log_level.upper()])

video_typer = typer.Typer(help="Video commands", callback=global_callback)

cli = typer.Typer(callback=global_callback)
cli.add_typer(video_typer, name="video")

@video_typer.command(
    "populate", 
    help="Populate the videos database from youtube/youtube-videos.json list",
)
def populate_videos_database(drop_db_first: bool = False):
    svc = get_default_video_processing_service()
    svc.populate_default_videos(drop_db_first=drop_db_first)

@video_typer.command(
    "search", 
    help="Find videos in the database using semantic search",
)
def search_videos(query: str):
    results = get_default_video_search_service().search(query)
    output_search_results(results)

@video_typer.command(
    "create", 
    help="Create a video in the database",
)
def create_video(
    id: str = typer.Option(..., help="ID of the YouTube video, hash part of the url"),
    title: str = typer.Option(..., help="Title of the YouTube video"),
    meta: str = typer.Option( 
        default="{}",
        help="Metadata for the video as json string",
    )
):
    video = Video(id=id, title=title, meta=json.loads(meta))
    svc = get_default_video_processing_service()
    svc.process_video(video)

@video_typer.command(
    "list", 
    help="List all videos in the database",
)
def list_videos():
    videos = get_default_video_crud().list_videos()

    table = get_video_table()
    for video in videos:
        output_video(video, table, console_print=False)

    console.print(table)

@video_typer.command(
    "get", 
    help="Get a video from the database",
)
def get_video(video_id: int):
    video = get_default_video_crud().get_video(video_id)
    output_video(video)

@video_typer.command(
    "export-all", 
    help="Export all videos to a json file",
)
def export_videos(file_path: Path = typer.Option(..., help="Relative path to the json file")):
    file_path = Path(__file__).resolve().parent / file_path
    svc = get_default_video_processing_service()
    svc.export_videos_as_json_file(file_path)
    logging.getLogger(__name__).info(f"Exported video data from DB to {file_path}")

def get_video_table():
    table = Table(show_header=True, header_style="bold magenta")

    table.add_column("ID")
    table.add_column("Title")
    table.add_column("URL")
    table.add_column("Meta")

    return table

def output_video(video: Video, table: Table | None = None, console_print: bool = True):
    table = table or get_video_table()
    table.add_row(str(video.internal_id), video.title, video.url, json.dumps(video.meta))
    if console_print:
        console.print(table)

def output_search_results(results: list[SearchResultChunk]):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Document Title")
    table.add_column("Document URL")
    table.add_column("Snippet")
    table.add_column("Distance")
    table.add_column("Start Time")
    table.add_column("End Time")

    for result in results:
        table.add_row(
            result.document_title,
            result.document_url,
            result.text[:100]+ " ... (truncated)",
            f"{result.distance:.2f}",
            str(result.start_ts),
            str(result.end_ts),
        )

    console.print(table)

if __name__ == "__main__":
    cli()
