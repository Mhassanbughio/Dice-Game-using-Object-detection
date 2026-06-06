import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO 
import os
#
#/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Assignment_3_494962
#/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Assignment_3_494962/best.pt
# Load the trained YOLOv8 model /Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Assignment_3_494962
#model = YOLO('D:\\NUST\\DeepLearning\\Assignment 3\\best.pt') 
#model = YOLO('D:/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Assignment_3_494962/best.pt')
#model = YOLO('/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Assignment_3_494962/best.pt')

#from ultralytics import YOLO
from pathlib import Path

model_path = Path.home() / "Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Assignment_3_494962/best.pt"
model = YOLO(str(model_path))

class DiceGame:
    def __init__(self, root, image_folder):
        self.root = root
        self.image_folder = image_folder
        self.image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.jpg')])
        self.current_image_index = 0
        self.total_score = 0
        self.uploaded_image_path = None
        self.game_over = False
        self.dice_values = []

        # Configure root window
        self.root.configure(bg="#F0F4F8")  # Light gray-blue background
        self.root.title("Dice Game Scoring System")
        self.root.geometry("700x600")

        # Title Label
        self.title_label = tk.Label(root, text="🎲 Dice Scoring Game 🎲", font=("Comic Sans MS", 28, "bold"),
                                    fg="#2C3E50", bg="#F0F4F8")
        self.title_label.pack(pady=15)

        # Frame for Image Display
        self.image_frame = tk.Frame(root, bg="#FFFFFF", bd=5, relief="sunken")
        self.image_frame.pack(pady=10)
        self.image_label = tk.Label(self.image_frame, bg="#FFFFFF")
        self.image_label.pack()

        # Dice Values and Score Frame
        self.info_frame = tk.Frame(root, bg="#F0F4F8")
        self.info_frame.pack(pady=10)

        self.dice_label = tk.Label(self.info_frame, text="Dice: -- + --", font=("Comic Sans MS", 16),
                                   fg="#E67E22", bg="#F0F4F8")
        self.dice_label.pack()

        self.score_label = tk.Label(self.info_frame, text="Total Score: 0", font=("Comic Sans MS", 18, "bold"),
                                    fg="#E74C3C", bg="#F0F4F8")
        self.score_label.pack()

        # Progress Label
        self.progress_label = tk.Label(root, text=f"Round: 0/{len(self.image_files)}", font=("Comic Sans MS", 14),
                                       fg="#7F8C8D", bg="#F0F4F8")
        self.progress_label.pack()

        # Button Frame with ttk for styling
        self.button_frame = tk.Frame(root, bg="#F0F4F8")
        self.button_frame.pack(pady=20)

        # Use ttk for better button styling
        style = ttk.Style()
        style.configure("TButton", font=("Comic Sans MS", 12, "bold"), padding=10)

        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.reset_game, style="TButton")
        self.start_button.grid(row=0, column=0, padx=10)

        self.score_button = ttk.Button(self.button_frame, text="Score", command=self.score_roll, style="TButton",
                                       state=tk.DISABLED)
        self.score_button.grid(row=0, column=1, padx=10)

        self.upload_button = ttk.Button(self.button_frame, text="Upload Image", command=self.upload_image,
                                        style="TButton")
        self.upload_button.grid(row=0, column=2, padx=10)

    def reset_game(self):
        self.total_score = 0
        self.current_image_index = 0
        self.uploaded_image_path = None
        self.game_over = False
        self.dice_values = []
        self.score_label.config(text="Total Score: 0")
        self.dice_label.config(text="Dice: -- + --")
        self.progress_label.config(text=f"Round: 0/{len(self.image_files)}")
        self.image_label.config(image='')
        self.score_button.config(state=tk.NORMAL)
        messagebox.showinfo("Game Reset", "Game has been reset. Please upload an image or press 'Score' to proceed.")

    def display_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

        # Maintain aspect ratio
        original_width, original_height = image.size
        target_width, target_height = 450, 350
        aspect_ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * aspect_ratio)
        new_height = int(original_height * aspect_ratio)

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)
        self.image_label.config(image=image)
        self.image_label.image = image

    def process_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            messagebox.showerror("File Error", "Unable to open image.")
            return

        results = model(img)
        detections = results[0].boxes

        conf_threshold = 0.5
        detections = [d for d in detections if float(d.conf) > conf_threshold]

        if len(detections) != 2:
            messagebox.showerror("Detection Error", "Exactly two dice must be detected.")
            return

        self.dice_values = [int(d.cls) + 1 for d in detections]
        self.dice_label.config(text=f"Dice: {self.dice_values[0]} + {self.dice_values[1]}")

        if self.dice_values[0] == self.dice_values[1]:
            messagebox.showinfo("Game Over", f"Both dice show {self.dice_values[0]}. Game Over!\nTotal Score: {self.total_score}")
            self.score_button.config(state=tk.DISABLED)
            self.game_over = True
        else:
            sum_values = sum(self.dice_values)
            self.total_score += sum_values
            self.score_label.config(text=f"Total Score: {self.total_score}")

    def score_roll(self):
        if self.uploaded_image_path:
            self.process_image(self.uploaded_image_path)
            self.display_image(self.uploaded_image_path)
            self.uploaded_image_path = None
        elif self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
            self.process_image(image_path)
            self.display_image(image_path)
            self.current_image_index += 1
            self.progress_label.config(text=f"Round: {self.current_image_index}/{len(self.image_files)}")
        else:
            messagebox.showinfo("Game Over", "No more images to process.")

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png"), ("All Files", "*.*")]
        )
        if file_path:
            if self.game_over:
                messagebox.showinfo("Game Over", "The game is over. Please press 'Start' to reset the game.")
                return

            self.uploaded_image_path = file_path
            self.display_image(file_path)

            if not self.game_over:
                self.score_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    image_folder = "/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Double Dice Dataset/test"
    game = DiceGame(root, image_folder)
    root.mainloop()
    #/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03
    #image_folder = "D:\\NUST\\DeepLearning\\Assignment 3\\dataset\\images"
    #"/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03/Double Dice Dataset/test"
    #image_folder = "/Users/muhammadhassanbughio/Documents/NUST/S-2/Dr Adeel Mumtaz DL/Assignment/Assignment_03"
