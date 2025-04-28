# Best Practices for Using Images in the Project

## 1. Folder Structure

- **Static Images:**
  - Place all static images in the `static/images/` directory, organized by subfolders:
    - `general/` for images used across multiple pages (logos, icons, etc.)
    - `{{page}}/` for images specific to a page (e.g., `home/`, `about/`, etc.)
  - Example path: `static/images/general/logo.png` or `static/images/home/hero-dog.jpg`
- **User Uploads:**
  - User-uploaded images should be stored in the `static/uploads/` directory or a dedicated `media/` directory if using Django's media handling.

## 2. Referencing Images in Templates

- **Django Templates:**
  - Use the `{% static %}` template tag (make sure to `{% load static %}` at the top):
    ```django
    {% load static %}
    <img src="{% static 'images/home/hero-dog.jpg' %}" alt="Example Image">
    <img src="{% static 'images/general/logo.png' %}" alt="Logo">
    ```
- **Jinja2 Templates:**
  - Use the direct static path:
    ```html
    <img src="/static/images/home/hero-dog.jpg" alt="Example Image">
    <img src="/static/images/general/logo.png" alt="Logo">
    ```
  - Or, if your Jinja2 environment supports it, use:
    ```html
    <img src="{{ url_for('static', filename='images/home/hero-dog.jpg') }}" alt="Example Image">
    <img src="{{ url_for('static', filename='images/general/logo.png') }}" alt="Logo">
    ```
- This ensures that the correct URL is generated, regardless of your static files configuration.

## 3. Handling User Uploads

- For user-uploaded images, use Django's `MEDIA_URL` and `MEDIA_ROOT` settings.
- Reference uploaded images using the appropriate media path:

  ```html
  <img src="{{ user.profile_image.url }}" alt="User Profile Image">
  ```

## 4. Naming Conventions

- Use lowercase letters, numbers, and hyphens (`-`) for file names (e.g., `pet-photo-1.jpg`).
- Avoid spaces and special characters in file names.

## 5. Image Optimization

- Optimize images before uploading to reduce file size and improve load times.
- Use appropriate formats:
  - PNG for graphics and icons
  - JPG for photos
  - SVG for vector images

## 6. Version Control

- Keep a `.gitkeep` file in each image subfolder (e.g., `static/images/general/`, `static/images/home/`) to ensure they are tracked by git, even if empty.
- Do **not** commit large or unnecessary images to the repository.

## 7. Example Directory Structure

```
static/
  images/
    general/
      logo.png
      icon.svg
    home/
      hero-dog.jpg
      caso-toretto.jpg
    about/
      team.jpg
  uploads/
    user123_profile.jpg
```

## 8. Summary

- Use `static/images/general/` for shared assets and `static/images/{{page}}/` for page-specific assets. Reference them with the appropriate method for your template engine.
- Use `uploads/` or `media/` for user-generated content.
- Follow naming and optimization best practices for maintainability and performance. 