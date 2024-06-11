import os
from tkinter import Tk, filedialog, Label, Button, messagebox, Frame, Checkbutton, IntVar
from PIL import Image, ImageOps, ImageChops

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        # Set the window size
        window_width = 600
        window_height = 400

        # Get the screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate the position to center the window
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        # Set the position and size of the window
        root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Create a frame for better aesthetics
        frame = Frame(root, padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        self.label = Label(frame, text="Select a folder containing images", font=("Helvetica", 14))
        self.label.pack(pady=10)

        self.select_folder_button = Button(frame, text="Select Source Folder", command=self.select_source_folder, font=("Helvetica", 12), bg="lightblue")
        self.select_folder_button.pack(pady=10)

        self.output_folder_button = Button(frame, text="Select Output Folder", command=self.select_output_folder, font=("Helvetica", 12), bg="lightblue")
        self.output_folder_button.pack(pady=10)

        self.save_to_source_var = IntVar()
        self.save_to_source_check = Checkbutton(frame, text="Save small icons to the source folder", variable=self.save_to_source_var, font=("Helvetica", 12))
        self.save_to_source_check.pack(pady=10)

        self.process_button = Button(frame, text="Process Images", command=self.process_images, font=("Helvetica", 12), bg="lightgreen")
        self.process_button.pack(pady=10)

        self.image_files = []
        self.source_folder = ''
        self.output_folder = ''

    def select_source_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.source_folder = folder_path
            self.populate_file_list(folder_path)
            messagebox.showinfo("Info", f"Source folder selected: {folder_path}")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder = folder_path
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
        else:
            messagebox.showwarning("Warning", "No images found in the selected folder.")

    def process_images(self):
        if not self.image_files:
            messagebox.showerror("Error", "No images to process. Please select a source folder first.")
            return

        if not self.output_folder and not self.save_to_source_var.get():
            messagebox.showerror("Error", "No output folder selected. Please select an output folder or choose to save small icons to the source folder.")
            return

        for file_path in self.image_files:
            try:
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

                # Save the image to the output folder
                if self.output_folder:
                    output_path = os.path.join(self.output_folder, os.path.basename(file_path))
                    final_img.save(output_path, quality=100)

                # Save the image to the source folder with "-sm" appended to the filename
                if self.save_to_source_var.get():
                    base, ext = os.path.splitext(file_path)
                    output_path_sm = base + "-sm" + ext
                    final_img.save(output_path_sm, quality=100)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {file_path}: {e}")

        messagebox.showinfo("Success", "Images have been processed and saved.")

if __name__ == "__main__":
    root = Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
