from django.db import models

class SystemApp(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('Personal Project', 'Personal Project'),
        ('Client Project', 'Client Project'),
        ('Startup', 'Startup'),
    ]

    app_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='icons/') 
    
    description = models.TextField(blank=True, null=True, help_text="Project overview")
    tech_stack = models.CharField(max_length=255, blank=True, null=True)
    frontend_repo = models.URLField(blank=True, null=True, help_text="GitHub Frontend Link")
    backend_repo = models.URLField(blank=True, null=True, help_text="GitHub Backend Link")
    live_link = models.URLField(blank=True, null=True, help_text="Live Hosted URL")
    
    project_type = models.CharField(
        max_length=50, 
        choices=PROJECT_TYPE_CHOICES, 
        default='Personal Project',
        help_text="Categorize this application"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SystemOS(models.Model):
    icon = models.ImageField(upload_to='system_icons/', null=True, blank=True)
    
    project_name = models.CharField(max_length=200, default="My Portfolio OS")
    frontend_engine = models.CharField(max_length=200, blank=True, null=True)
    backend_architecture = models.CharField(max_length=200, blank=True, null=True)
    database_system = models.CharField(max_length=200, blank=True, null=True)
    active_libraries = models.TextField(blank=True, null=True)
    hosting_environment = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name
    
    class Meta:
        verbose_name_plural = "System OS Info"


# --- NEW: About Us / Profile Model ---
class AboutMe(models.Model):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Social Links
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    x_url = models.URLField(blank=True, null=True, help_text="Twitter / X URL")
    instagram_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True, help_text="Contact email address")

    resume = models.FileField(upload_to='resumes/', blank=True, null=True, help_text="Upload your Resume/CV (PDF recommended)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"About: {self.name}"
    
    class Meta:
        verbose_name_plural = "About Me Info"