import os
from tkinter import Tk, filedialog, Label, Button, messagebox
from PIL import Image, ImageOps

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        self.label = Label(root, text="Select a folder containing images")
        self.label.pack()

        self.select_folder_button = Button(root, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

        self.process_button = Button(root, text="Process Images", command=self.process_images)
        self.process_button.pack()

        self.image_files = []

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_file_list(folder_path)

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
            messagebox.showerror("Error", "No images to process. Please select a folder first.")
            return

        output_folder = filedialog.askdirectory(title="Select Output Folder")
        if not output_folder:
            messagebox.showerror("Error", "No output folder selected.")
            return

        for file_path in self.image_files:
            try:
                img = Image.open(file_path)
                img = img.convert("RGBA")

                # Calculate the new size with padding
                new_size = (img.width + 50, img.height + 50)

                # Create a new transparent image with padding
                new_img = Image.new("RGBA", new_size, (255, 255, 255, 0))
                new_img.paste(img, (25, 25), img)

                # Resize the image to 200x200
                new_img = new_img.resize((200, 200), Image.LANCZOS)

                # Save the image
                output_path = os.path.join(output_folder, os.path.basename(file_path))
                new_img.save(output_path, quality=100)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {file_path}: {e}")

        messagebox.showinfo("Success", "Images have been processed and saved.")

if __name__ == "__main__":
    root = Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
