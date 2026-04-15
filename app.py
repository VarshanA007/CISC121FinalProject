# Varshan Akhilan
# Project Step 3 

import gradio as gr
import time


def get_merge_sort_snapshots(queue):
    
    # Sorts a list of submitted values by 'submitted_at' using Merge Sort.
    # Saves and returns the  the list after every movement, which is used later for the GUI animation.
    
    snapshots = []
    
    # Creating a temporary copy 
    arr = queue.copy()
    
    #  Appending the unsorted state as the first snapshot
    snapshots.append(list(arr))

    def merge(A, left, mid, right):
        left_sub = A[left:mid + 1]
        right_sub = A[mid + 1:right + 1]
        
        i = 0 # left_sub
        j = 0 # right_sub
        k = left # main array A
        
        while i < len(left_sub) and j < len(right_sub):
            # Comparing the timestamps 
            if left_sub[i]['submitted_at'] <= right_sub[j]['submitted_at']:
                A[k] = left_sub[i]
                i += 1
            else:
                A[k] = right_sub[j]
                j += 1
            k += 1
            
            # Recording the state after a move
            snapshots.append(list(A))

        # Copy any left over elements
        while i < len(left_sub):
            A[k] = left_sub[i]
            i += 1
            k += 1
            snapshots.append(list(A))
            
        while j < len(right_sub):
            A[k] = right_sub[j]
            j += 1
            k += 1
            snapshots.append(list(A))

    def merge_sort(A, left, right):
        if left < right:
            mid = (left + right) // 2
            merge_sort(A, left, mid)
            merge_sort(A, mid + 1, right)
            merge(A, left, mid, right)
            
    if len(arr) > 1:
        merge_sort(arr, 0, len(arr) - 1)
    
    return snapshots, arr

# GRADIO UI CODE, MAINLY DONE BY GEMINI (as declared in project README file with some minor adjustments by me)

# Initial dummy data so the user has something to sort right away
initial_queue = [
    {"student_id": "10293847", "submitted_at": "14:30", "file_name": "a1_p1.py"},
    {"student_id": "10293848", "submitted_at": "09:15", "file_name": "a1_p2.py"},
    {"student_id": "10293849", "submitted_at": "11:45", "file_name": "a1_p1.py"},
    {"student_id": "10293850", "submitted_at": "08:00", "file_name": "a1_p3.py"}
]

def add_submission(student_id, time_str, filename, current_queue):
    """Handles adding a new submission and updating the state."""
    # Basic input validation
    if not student_id or not time_str or not filename:
        raise gr.Error("Please fill out all fields before adding.")
        
    new_sub = {"student_id": student_id, "submitted_at": time_str, "file_name": filename}
    current_queue.append(new_sub)
    return current_queue, current_queue

def animate_sorting(current_queue):
    """Yields frames one by one to create an animation effect in Gradio."""
    frames, sorted_queue = get_merge_sort_snapshots(current_queue)
    
    # Step through each snapshot and yield it to the UI with a delay
    for i, frame in enumerate(frames):
        # Format as a list of lists for the Gradio Dataframe
        display_data = [[row["student_id"], row["submitted_at"], row["file_name"]] for row in frame]
        yield display_data, current_queue
        time.sleep(0.8) # Adjust this to make the animation faster/slower
        
    # Update the underlying state to the final sorted version
    current_queue.clear()
    current_queue.extend(sorted_queue)

# ==========================================
# GUI LAYOUT
# ==========================================
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📋 TA Grading Queue Organizer")
    gr.Markdown("Watch Merge Sort organically organize incoming student submissions by their timestamp.")
    
    # State variable to hold the queue data in memory
    queue_state = gr.State(initial_queue)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Add New Submission")
            stu_id_input = gr.Textbox(label="Student ID", placeholder="e.g., 10345678")
            time_input = gr.Textbox(label="Submission Time (HH:MM)", placeholder="e.g., 15:45")
            file_input = gr.Textbox(label="File Name", placeholder="e.g., assignment.py")
            add_btn = gr.Button("➕ Add Submission", variant="secondary")
            
            sort_btn = gr.Button("🚀 Animate Merge Sort", variant="primary")
            
        with gr.Column():
            gr.Markdown("### Live Grading Queue")
            # Convert initial state to nested lists for the dataframe
            initial_df_data = [[row["student_id"], row["submitted_at"], row["file_name"]] for row in initial_queue]
            
            queue_display = gr.Dataframe(
                headers=["Student ID", "Submitted At", "File Name"],
                datatype=["str", "str", "str"],
                value=initial_df_data,
                interactive=False
            )

    # Event Listeners
    add_btn.click(
        fn=add_submission,
        inputs=[stu_id_input, time_input, file_input, queue_state],
        outputs=[queue_state, queue_display]
    )
    
    sort_btn.click(
        fn=animate_sorting,
        inputs=[queue_state],
        outputs=[queue_display, queue_state]
    )

if __name__ == "__main__":
    demo.launch()