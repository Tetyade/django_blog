# 🌟 Django Social Blog

A modern social blogging platform built with Python and Django. This project combines classic blogging features with social networking capabilities, allowing users to share content, message each other, follow interesting authors, and interact in real-time.

![Home Feed](screenshots/home_feed.png)
*(Screenshot: Main Feed)*

## 🚀 Key Features

### 👤 Authentication & Profiles
- **Secure Auth:** User registration, login, and password reset functionality.
- **User Profiles:** Customizable profiles with avatars, bio, and personal stats.
- **Stats:** Track "Followers" and "Following" counts.
- **Profile Editing:** Easy-to-use form to update personal information.

### 📝 Content & Posts
- **CRUD Operations:** Create, Read and Delete posts.
- **Media Support:** Upload images for posts with instant preview before publishing.
- **Smart Feed:** Dynamic feed displaying posts from followed users and general content.

### ❤️ Social Interaction (AJAX)
- **Instant Likes:** Like posts and comments without page reloads.
- **Comments:** Discuss posts with a threaded comment system.
- **Follow System:** Follow/Unfollow users to curate your feed.
- **Live Search:** Search for users by username with instant results and "Follow" buttons directly in the search dropdown.

### 💬 Communication
- **Direct Messages:** Private one-on-one chat threads.
- **Group Chats:** Create and manage group conversations.
- **Notifications:** Real-time alerts for likes, new followers, and messages.

## 🛠 Tech Stack

- **Backend:** Python 3, Django 5.x
- **Database:** SQLite (default) / PostgreSQL (compatible)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API for AJAX)
- **Icons:** Bootstrap Icons
- **Media Handling:** Pillow (Image processing)

## 📸 Screenshots

### User Profile
A stylish profile card featuring user stats and action buttons.
![User Profile](screenshots/user_profile.png)

### Live Search
Find users instantly and follow them without leaving the page.
![Search Demo](screenshots/search_demo.png)

### Messaging System
Clean interface for direct messages and group chats.
![Chat View](screenshots/chat_view.png)

### Create Post
User-friendly form with image preview support.
![Create Post](screenshots/create_post.png)

## ⚙️ Installation & Setup

Follow these steps to run the project locally:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/django-social-blog.git](https://github.com/your-username/django-social-blog.git)
   cd django-social-blog

2. **Create a virtual environment:**
    ```bash
   # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

3. **Install dependencies:**
    ```bash
   pip install -r requirements.txt

4. **Apply migrations:**
    ```bash
   python manage.py migrate

5. **Create a superuser (optional, for Admin Panel):**
    ```bash
   python manage.py createsuperuser

6. **Run the server:**
    ```bash
   python manage.py runserver

7. **Access the app:** Open your browser and go to http://127.0.0.1:8000/

## 📂 Project Structure

- **`posts/`**: Core logic for posts, feed, and likes.
- **`auth_system/`**: User authentication, registration, and profile management.
- **`comments/`**: Commenting system logic.
- **`messages/`**: Direct messaging and chat threads.
- **`groups/`**: Group chat functionality.
- **`notifications/`**: User notification system.
- **`templates/`**: HTML templates organized by app.
- **`static/`**: CSS styles, JavaScript files, and images.
