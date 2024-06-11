import os
from tkinter import Tk, filedialog, messagebox, Frame, IntVar, StringVar, Canvas, Toplevel, Scrollbar
from tkinter import ttk
from PIL import Image, ImageOps, ImageChops, ImageTk

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        # Set the window size
        window_width = 700
        window_height = 500

        # Get the screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate the position to center the window
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        # Set the position and size of the window
        root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Apply a modern theme
        style = ttk.Style()
        style.theme_use("clam")  # Using 'clam' theme for a modern look

        # Create a frame for better aesthetics
        frame = ttk.Frame(root, padding="20 20 20 20")
        frame.pack(fill='both', expand=True)

        self.label = ttk.Label(frame, text="Select a folder containing images", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.select_folder_button = ttk.Button(frame, text="Select Source Folder", command=self.select_source_folder, style="TButton")
        self.select_folder_button.pack(pady=10)

        self.source_folder_var = StringVar(value="Source folder: None selected")
        self.source_folder_label = ttk.Label(frame, textvariable=self.source_folder_var, font=("Helvetica", 12))
        self.source_folder_label.pack(pady=10)

        self.output_folder_button = ttk.Button(frame, text="Select Output Folder", command=self.select_output_folder, style="TButton")
        self.output_folder_button.pack(pady=10)

        self.output_folder_var = StringVar(value="Output folder: None selected")
        self.output_folder_label = ttk.Label(frame, textvariable=self.output_folder_var, font=("Helvetica", 12))
        self.output_folder_label.pack(pady=10)

        self.process_button = ttk.Button(frame, text="Process Images", command=self.preview_images, style="TButton")
        self.process_button.pack(pady=20)

        self.image_files = []
        self.source_folder = ''
        self.output_folder = ''
        self.previews = []  # Store references to image previews to prevent garbage collection

    def select_source_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.source_folder = folder_path
            self.source_folder_var.set(f"Source folder: {folder_path}")
            self.populate_file_list(folder_path)
            messagebox.showinfo("Info", f"Source folder selected: {folder_path}")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder = folder_path
            self.output_folder_var.set(f"Output folder: {folder_path}")
            messagebox.showinfo("Info", f"Output folder selected: {folder_path}")

    def populate_file_list(self, folder_path):
        self.image_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                    full_path = os.path.join(root, file)
                    self.image_files.append(full_path)

        if self.image_files:
            messagebox.showinfo("Info", f"Found {len(self.image_files)} images to process.")
            print(f"Debug: Found images: {self.image_files}")
        else:
            messagebox.showwarning("Warning", "No images found in the selected folder.")
            print("Debug: No images found.")

    def process_image(self, file_path):
        img = Image.open(file_path)
        img = img.convert("RGBA")

        # Crop the image to the bounding box of the non-transparent content
        bbox = ImageChops.difference(img, Image.new(img.mode, img.size)).getbbox()
        if bbox:
            img = img.crop(bbox)

        # Add a 25 pixel border with transparency around the main content
        new_img = ImageOps.expand(img, border=25, fill=(255, 255, 255, 0))

        # Resize the image to 200x200 while maintaining aspect ratio
        new_img.thumbnail((200, 200), Image.LANCZOS)

        # Create a new 200x200 image with a transparent background
        final_img = Image.new("RGBA", (200, 200), (255, 255, 255, 0))

        # Center the thumbnail on the 200x200 image
        final_img.paste(new_img, ((200 - new_img.width) // 2, (200 - new_img.height) // 2))

        return final_img

    def preview_images(self):
        if not self.image_files:
            messagebox.showerror("Error", "No images to process. Please select a source folder first.")
            return

        preview_window = Toplevel(self.root)
        preview_window.title("Preview Processed Images")

        # Set the window size
        window_width = 800
        window_height = 600

        # Get the screen dimensions
        screen_width = preview_window.winfo_screenwidth()
        screen_height = preview_window.winfo_screenheight()

        # Calculate the position to center the window
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        # Set the position and size of the window
        preview_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Create a frame for the canvas and scrollbar
        canvas_frame = ttk.Frame(preview_window)
        canvas_frame.pack(fill='both', expand=True)

        # Create a canvas with a scrollbar
        canvas = Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Create a scrollable frame inside the canvas
        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        y_position = 20
        self.previews = []  # Reset previews list
        for i, file_path in enumerate(self.image_files[:10]):
            before_img = Image.open(file_path)
            before_img.thumbnail((200, 200), Image.LANCZOS)
            before_photo = ImageTk.PhotoImage(before_img)
            self.previews.append(before_photo)  # Store reference to prevent garbage collection

            processed_img = self.process_image(file_path)
            processed_photo = ImageTk.PhotoImage(processed_img)
            self.previews.append(processed_photo)  # Store reference to prevent garbage collection

            self.draw_grid(canvas, y_position, 200, 200)

            canvas.create_image(20, y_position, anchor='nw', image=before_photo)
            canvas.create_text(230, y_position + 90, text="→", font=("Helvetica", 24))
            canvas.create_image(260, y_position, anchor='nw', image=processed_photo)

            y_position += 220

        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        confirm_button = ttk.Button(preview_window, text="Confirm", command=lambda: self.process_images(confirm=True, preview_window=preview_window))
        confirm_button.pack(pady=20)

    def draw_grid(self, canvas, y_position, width, height):
        step = 20
        for x in range(0, width + 1, step):
            canvas.create_line(x + 20, y_position, x + 20, y_position + height, fill="#ccc")
        for y in range(y_position, y_position + height + 1, step):
            canvas.create_line(20, y, 20 + width, y, fill="#ccc")
        for x in range(0, width + 1, step):
            canvas.create_line(x + 260, y_position, x + 260, y_position + height, fill="#ccc")
        for y in range(y_position, y_position + height + 1, step):
            canvas.create_line(260, y, 260 + width, y, fill="#ccc")

    def process_images(self, confirm=False, preview_window=None):
        if confirm:
            if preview_window:
                preview_window.destroy()

            if not self.output_folder:
                messagebox.showerror("Error", "No output folder selected. Please select an output folder.")
                return

            for file_path in self.image_files:
                try:
                    final_img = self.process_image(file_path)

                    # Save the image to the output folder with "-sm" appended to the filename
                    base, ext = os.path.splitext(os.path.basename(file_path))
                    output_path = os.path.join(self.output_folder, base + "-sm" + ext)
                    final_img.save(output_path, quality=100)

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process {file_path}: {e}")

            messagebox.showinfo("Success", "Images have been processed and saved.")

if __name__ == "__main__":
    root = Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
