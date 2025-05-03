import gradio as gr
import json
import re
import math
from typing import List, Dict, Any, Tuple

from app.services.search import get_default_video_search_service
from app.services.crud import get_default_video_crud
from app.storage.models import SearchResultChunk
from app.youtube.data_loader import Video

# YouTube thumbnail URL format
YOUTUBE_THUMBNAIL_URL = "https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
# YouTube video URL with timestamp
YOUTUBE_VIDEO_URL_WITH_TIMESTAMP = "https://www.youtube.com/watch?v={video_id}&t={timestamp}s"
# Default page size options
PAGE_SIZE_OPTIONS = [5, 10, 20, 50]
# Default page size
DEFAULT_PAGE_SIZE = 5

def extract_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL."""
    match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return ""

def format_time(seconds: float) -> str:
    """Format seconds into MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def format_metadata_as_tags(meta: dict) -> str:
    """Format metadata as a series of tag spans."""
    if not meta:
        return ""
    
    tags_html = '<div style="margin-top: 8px;">'
    for key, value in meta.items():
        value_str = str(value)
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        # Improved tag style with better contrast and visibility
        tags_html += f'<span style="display: inline-block; background-color: #e1f5fe; color: #01579b; border-radius: 16px; padding: 3px 10px; margin-right: 6px; margin-bottom: 6px; font-size: 12px; border: 1px solid #b3e5fc;"><strong style="color: #01579b;">{key}:</strong> {value_str}</span>'
    tags_html += '</div>'
    
    return tags_html

def get_rating_stars(distance: float) -> str:
    """Convert distance to star rating."""
    if distance <= 0.8:
        return "⭐⭐⭐⭐⭐ (Very strong match)"
    elif distance <= 1.2:
        return "⭐⭐⭐⭐ (Good relevance)"
    elif distance <= 1.6:
        return "⭐⭐⭐ (Moderate relevance)"
    elif distance <= 2.0:
        return "⭐⭐ (Weak relevance)"
    else:
        return "⭐ (Likely irrelevant)"

def video_to_html(video: Video) -> str:
    """Convert a video to HTML for display in Gradio."""
    video_id = extract_video_id(video.url)
    thumbnail_url = YOUTUBE_THUMBNAIL_URL.format(video_id=video_id)
    
    metadata_tags = format_metadata_as_tags(video.meta)
    
    return f"""
    <div style="display: flex; margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
        <div style="flex: 0 0 200px; margin-right: 15px;">
            <a href="{video.url}" target="_blank">
                <img src="{thumbnail_url}" alt="{video.title}" style="width: 100%; border-radius: 5px;">
            </a>
        </div>
        <div style="flex: 1;">
            <h3 style="margin-top: 0;"><a href="{video.url}" target="_blank" style="text-decoration: none; color: #1a73e8;">{video.title}</a></h3>
            <p>ID: {video.id}</p>
            {metadata_tags}
        </div>
    </div>
    """

def fetch_videos_paginated(page: int, page_size: int) -> Tuple[str, int, int, int]:
    """
    Fetch videos with server-side pagination.
    
    Args:
        page: Current page number (1-indexed)
        page_size: Number of videos per page
    
    Returns:
        Tuple containing:
        - HTML content
        - Total number of pages
        - Current page
        - Current page size
    """
    # Calculate offset based on page number and size
    offset = (page - 1) * page_size
    
    # Fetch videos with pagination from the database
    videos, total_count = get_default_video_crud().list_videos_paginated(limit=page_size, offset=offset)
    
    if not videos:
        return "<p>No videos found in the database.</p>", 0, 1, page_size
    
    # Calculate total pages
    total_pages = math.ceil(total_count / page_size)
    
    # Ensure page is within bounds
    page = max(1, min(page, total_pages))
    
    # Calculate current range for display
    start_idx = offset + 1
    end_idx = min(offset + page_size, total_count)
    
    html_content = f"<h2>Available Videos (Showing {start_idx}-{end_idx} of {total_count})</h2>"
    for video in videos:
        html_content += video_to_html(video)
    
    return html_content, total_pages, page, page_size

def search_results_to_html(results: List[SearchResultChunk]) -> str:
    """Convert search results to HTML for display in Gradio."""
    if not results:
        return "<p>No results found.</p>"
    
    html_content = "<h2>Search Results</h2>"
    
    for result in results:
        video_id = extract_video_id(result.document_url)
        thumbnail_url = YOUTUBE_THUMBNAIL_URL.format(video_id=video_id)
        video_with_timestamp = YOUTUBE_VIDEO_URL_WITH_TIMESTAMP.format(
            video_id=video_id, 
            timestamp=int(result.start_ts)
        )
        
        formatted_start = format_time(result.start_ts)
        formatted_end = format_time(result.end_ts)
        rating_stars = get_rating_stars(result.distance)
        
        html_content += f"""
        <div style="display: flex; margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
            <div style="flex: 0 0 200px; margin-right: 15px;">
                <a href="{video_with_timestamp}" target="_blank">
                    <img src="{thumbnail_url}" alt="{result.document_title}" style="width: 100%; border-radius: 5px;">
                </a>
            </div>
            <div style="flex: 1;">
                <h3 style="margin-top: 0;">
                    <a href="{video_with_timestamp}" target="_blank" style="text-decoration: none; color: #1a73e8;">
                        {result.document_title}
                    </a>
                </h3>
                <p><strong>Time:</strong> {formatted_start} - {formatted_end}</p>
                <p><strong>Relevance:</strong> {result.distance:.2f} - {rating_stars}</p>
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px; border: 1px solid #e1e4e8; color: #24292e;">
                    {result.text}
                </div>
            </div>
        </div>
        """
    
    return html_content

def search_videos(query: str, num_neighbors: int) -> str:
    """Search videos with the given query."""
    if not query.strip():
        return "<p>Please enter a search query.</p>"
    
    results = get_default_video_search_service().search(query, num_neighbors=num_neighbors)
    return search_results_to_html(results)

def create_ui() -> gr.Blocks:
    """Create the Gradio UI."""
    with gr.Blocks(css="footer {visibility: hidden}") as demo:
        gr.Markdown("# YouTube Semantic Search")
        
        with gr.Tab("Video List"):
            # State variables for pagination
            current_page = gr.State(1)
            total_pages = gr.State(1)
            current_page_size = gr.State(DEFAULT_PAGE_SIZE)
            
            # Content display
            videos_html = gr.HTML()
            
            # Pagination controls
            with gr.Row():
                prev_btn = gr.Button("← Previous")
                page_info = gr.Markdown("Page 1 of 1")
                next_btn = gr.Button("Next →")
                refresh_btn = gr.Button("Refresh")
            
            # Page size selector
            with gr.Row():
                page_size_dropdown = gr.Dropdown(
                    choices=[str(size) for size in PAGE_SIZE_OPTIONS],
                    value=str(DEFAULT_PAGE_SIZE),
                    label="Videos per page",
                    interactive=True
                )
            
            # Function to update page info text
            def update_page_info(page, total):
                return f"Page {page} of {total}"
            
            # Function to navigate pages
            def navigate_page(direction, current, total, page_size):
                if direction == "prev":
                    new_page = max(1, current - 1)
                else:  # next
                    new_page = min(total, current + 1)
                
                html, total_pages, current_page, current_page_size = fetch_videos_paginated(new_page, page_size)
                page_info_text = update_page_info(current_page, total_pages)
                
                return html, current_page, total_pages, current_page_size, page_info_text
            
            # Function to change page size
            def change_page_size(new_size_str, current_page):
                new_size = int(new_size_str)
                html, total_pages, current_page, current_page_size = fetch_videos_paginated(1, new_size)
                page_info_text = update_page_info(current_page, total_pages)
                
                return html, current_page, total_pages, current_page_size, page_info_text
            
            # Initial load function
            def init_videos():
                html, total_pages, current_page, current_page_size = fetch_videos_paginated(1, DEFAULT_PAGE_SIZE)
                page_info_text = update_page_info(current_page, total_pages)
                return html, current_page, total_pages, current_page_size, page_info_text
            
            # Connect buttons to functions
            prev_btn.click(
                lambda curr, total, size: navigate_page("prev", curr, total, size),
                inputs=[current_page, total_pages, current_page_size],
                outputs=[videos_html, current_page, total_pages, current_page_size, page_info]
            )
            
            next_btn.click(
                lambda curr, total, size: navigate_page("next", curr, total, size),
                inputs=[current_page, total_pages, current_page_size],
                outputs=[videos_html, current_page, total_pages, current_page_size, page_info]
            )
            
            refresh_btn.click(
                init_videos,
                outputs=[videos_html, current_page, total_pages, current_page_size, page_info]
            )
            
            page_size_dropdown.change(
                change_page_size,
                inputs=[page_size_dropdown, current_page],
                outputs=[videos_html, current_page, total_pages, current_page_size, page_info]
            )
        
        with gr.Tab("Search Videos"):
            with gr.Row():
                search_input = gr.Textbox(label="Search Query", placeholder="Enter your search query...")
                neighbors_slider = gr.Slider(
                    minimum=1, 
                    maximum=20, 
                    value=5, 
                    step=1, 
                    label="Number of Results",
                    info="How many search results to return"
                )
                search_btn = gr.Button("Search")
            
            results_html = gr.HTML()
            search_btn.click(fn=search_videos, inputs=[search_input, neighbors_slider], outputs=results_html)
        
        # Initialize with the video list
        demo.load(
            init_videos,
            outputs=[videos_html, current_page, total_pages, current_page_size, page_info]
        )
    
    return demo

def main():
    """Run the Gradio app."""
    app = create_ui()
    app.launch(server_name="0.0.0.0")

if __name__ == "__main__":
    main() 