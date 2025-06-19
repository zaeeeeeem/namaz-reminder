<div align="center">
  <img src="./app/assets/icon.png" alt="Namaz Reminder Logo" width="150"/>
  <h1>Namaz Reminder & Islamic Assistant</h1>
  <p>
    A modern, feature-rich desktop application designed to provide timely prayer notifications, an AI-powered Islamic knowledge base, and prayer tracking capabilities.
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
    <img src="https://img.shields.io/badge/Status-Active-green.svg" alt="Status">
  </p>
</div>

---

## ✨ Key Features

* **⏰ Accurate Prayer Notifications:** Set your local prayer times and receive timely, interactive desktop notifications with an audible Azan.
* **🤖 AI Islamic Assistant:** Integrated with Google's Gemini API, ask questions on various Islamic topics and get helpful, context-aware answers.
* **🗓️ 7-Day Prayer Calendar:** Visually track your prayer consistency and log the status of each prayer (Completed, Late, Not Completed).
* **⚙️ Persistent Background Operation:** Minimize the application to the system tray to ensure the reminder service is always running without cluttering your desktop.
* **🎨 Modern & Clean UI:** Built with CustomTkinter for a sleek, modern, and user-friendly experience.
* **📦 Standalone Executable:** Packaged with PyInstaller for easy distribution and use on Windows without needing to install Python or any dependencies.

---

## 📸 Screens

<table width="100%">
  <tr>
    <td width="50%" align="center">
      <b>AI Islamic Assistant</b><br>
    </td>
    <td width="50%" align="center">
      <b>Prayer Tracking Calendar</b><br>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <b>Notification Popup</b><br>
    </td>
    <td width="50%" align="center">
      <b>System Tray Menu</b><br>
    </td>
  </tr>
</table>

---

## 🛠️ Technology Stack

* **Language:** Python 3.11+
* **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Audio Playback:** [Pygame](https://www.pygame.org/news)
* **System Tray:** [Pystray](https://github.com/moses-palmer/pystray)
* **Image Processing:** [Pillow](https://python-pillow.org/)
* **AI Service:** [Google Gemini API](https://ai.google.dev/)
* **Deployment:** [PyInstaller](https://pyinstaller.org/en/stable/)
* **Version Control:** Git & GitHub

---

## 🏗️ Project Architecture

The project follows a clean, layered architecture based on the **Separation of Concerns** principle. This makes the codebase modular, maintainable, and easy to scale.

```
namaz-reminder/
├── app/
│   ├── models/         # Data storage schemas (JSON files)
│   ├── services/       # Background logic & external API clients
│   ├── utils/          # Shared utilities & configuration
│   └── views/          # All UI components and views
├── assets/             # Icons, sounds, and other media
├── main.py             # Main entry point of the application
├── requirements.txt    # Project dependencies
└── .env                # Environment variables (API keys)
```

---

## 🚀 Getting Started

Follow these instructions to set up the development environment and run the project on your local machine.

### Prerequisites

* **Python 3.11 or higher:** [Download Python](https://www.python.org/downloads/)
* **Git:** [Download Git](https://git-scm.com/downloads)

### Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/namaz-reminder.git](https://github.com/your-username/namaz-reminder.git)
    cd namaz-reminder
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    * Create a file named `.env` in the root directory of the project.
    * Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/).
    * Add your API key to the `.env` file:
        ```env
        GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```

### Running the Application

Once the setup is complete, you can run the application from the root directory:

```bash
python main.py
```

---

## 📦 Deployment

To build a standalone `.exe` file for Windows, use the following PyInstaller command from the root directory:

```bash
python -m PyInstaller --name "Namaz Reminder" --onefile --windowed --icon="app/assets/app_icon.ico" --add-data="app/assets;assets" --hidden-import="pystray.backend.win32" main.py
```
* `--onefile`: Bundles everything into a single executable.
* `--windowed`: Prevents the terminal from opening in the background.
* `--icon`: Sets the application icon.
* `--add-data`: Ensures the `assets` folder is included in the package.

The final executable will be located in the `dist` folder.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the application, please follow this workflow:

1.  **Fork the Repository:** Create your own copy of the project.
2.  **Create a Feature Branch:** `git checkout -b feature/YourAmazingFeature`
3.  **Commit Your Changes:** `git commit -m 'Add some amazing feature'`
4.  **Push to the Branch:** `git push origin feature/YourAmazingFeature`
5.  **Open a Pull Request:** Create a PR to merge your changes into the `staging-area` branch for review.

Please write clear commit messages and ensure your code follows the project's existing style.


---
<div align="center">
  <p>Developed with ❤️ by Zaeem, Arslan, Ahad, Amna</p>
</div>
