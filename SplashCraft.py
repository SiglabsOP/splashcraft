import os
from tkinter import Tk, filedialog, Button, Label, OptionMenu, StringVar, Entry, messagebox
from PIL import Image, UnidentifiedImageError

def add_watermark(directory, logo_path, position, new_directory, padding, scale, transparent=False):
  
    EXTS = ('.jpg', '.jpeg', '.png')

    try:
        original_logo = Image.open(logo_path)
    except UnidentifiedImageError:
        print(f"Failed to read logo from {logo_path}. Ensure it's a valid image format.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Convert logo to RGBA to ensure transparency handling    (c) SIG LABS 2024
    if original_logo.mode != 'RGBA':
        original_logo = original_logo.convert('RGBA')

    logo_mask_original = original_logo.split()[3] if original_logo.mode == 'RGBA' else None

    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(EXTS) and filename != os.path.basename(logo_path):
                full_path = os.path.join(dirpath, filename)
                try:
                    image = Image.open(full_path)
                except UnidentifiedImageError:
                    print(f"Skipped {filename}. Unsupported image format.")
                    continue
                except Exception as e:
                    print(f"An error occurred while processing {filename}: {e}")
                    continue

                image_width, image_height = image.size
                shorter_side = min(image_width, image_height)
                new_logo_width = int(shorter_side * scale / 100)
                logo_aspect_ratio = original_logo.width / original_logo.height
                new_logo_height = int(new_logo_width / logo_aspect_ratio)

                # Resize the logo and its mask
                logo = original_logo.resize((new_logo_width, new_logo_height))
                logo_mask = logo_mask_original.resize((new_logo_width, new_logo_height)) if logo_mask_original else None

                paste_x, paste_y = 0, 0

                if position == 'topleft':
                    paste_x, paste_y = padding, padding
                elif position == 'topright':
                    paste_x, paste_y = image_width - new_logo_width - padding, padding
                elif position == 'bottomleft':
                    paste_x, paste_y = padding, image_height - new_logo_height - padding
                elif position == 'bottomright':
                    paste_x, paste_y = image_width - new_logo_width - padding, image_height - new_logo_height - padding
                elif position == 'center':
                    paste_x, paste_y = (image_width - new_logo_width) // 2, (image_height - new_logo_height) // 2

                try:
                    if transparent:
                        image.paste(logo, (paste_x, paste_y), logo_mask)  # Paste with transparency
                    else:
                        image.paste(logo, (paste_x, paste_y))  # Paste normally
                except Exception as e:
                    print(f"An error occurred: {e}")

                relative_path = os.path.relpath(dirpath, directory)
                save_directory = new_directory if new_directory else directory
                final_save_directory = os.path.join(save_directory, relative_path)

                if not os.path.exists(final_save_directory):
                    os.makedirs(final_save_directory)

                new_image_path = os.path.join(final_save_directory, filename)
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                image.save(new_image_path)
                print(f'Added watermark to {new_image_path}')

    original_logo.close()


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watermarking Application")

        # Labels and buttons
        self.label_directory = Label(root, text="Select Source Directory")
        self.label_directory.pack()

        self.select_directory_button = Button(root, text="Select Directory", command=self.select_directory)
        self.select_directory_button.pack()

        self.label_logo = Label(root, text="Select Watermark Logo")
        self.label_logo.pack()

        self.select_logo_button = Button(root, text="Select Logo", command=self.select_logo)
        self.select_logo_button.pack()

        self.label_position = Label(root, text="Select Watermark Position")
        self.label_position.pack()

        self.position_var = StringVar(value="center")
        self.position_menu = OptionMenu(root, self.position_var, "topleft", "topright", "bottomleft", "bottomright", "center")
        self.position_menu.pack()

        self.label_padding = Label(root, text="Enter Padding (in pixels)")
        self.label_padding.pack()

        self.padding_entry = Entry(root)
        self.padding_entry.pack()

        self.label_scale = Label(root, text="Enter Scale (%)")
        self.label_scale.pack()

        self.scale_entry = Entry(root)
        self.scale_entry.pack()

        self.transparent_var = StringVar(value="no")
        self.transparent_checkbox = OptionMenu(root, self.transparent_var, "yes", "no")
        self.transparent_checkbox.pack()

        self.start_button = Button(root, text="Start Watermarking", command=self.start_watermarking)
        self.start_button.pack()

    def select_directory(self):
        self.directory = filedialog.askdirectory(title="Select Directory")
        print(f"Selected directory: {self.directory}")

    def select_logo(self):
        self.logo = filedialog.askopenfilename(title="Select Logo", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        print(f"Selected logo: {self.logo}")

    def start_watermarking(self):
        try:
            padding = int(self.padding_entry.get() or 0)
            scale = float(self.scale_entry.get() or 20)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid padding or scale value. Using default values.")
            padding = 0
            scale = 20

        transparent = self.transparent_var.get() == "yes"
        new_directory = self.directory  # Optionally change this to a different directory if needed.

        add_watermark(self.directory, self.logo, self.position_var.get(), new_directory, padding, scale, transparent)


if __name__ == "__main__":
    root = Tk()
    app = WatermarkApp(root)
    root.mainloop()
