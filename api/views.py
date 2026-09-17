# api/views.py
import os

from rest_framework.decorators import APIView, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SystemApp, SystemOS, AboutMe
from .serializers import SystemAppSerializer, SystemOSSerializer, AboutMeSerializer
from groq import Groq

@api_view(['GET'])
def get_system_apps(request):
    apps = SystemApp.objects.filter(is_active=True)
    serializer = SystemAppSerializer(apps, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_system_os(request):
    system_os_data = SystemOS.objects.all()
    serializer = SystemOSSerializer(system_os_data, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_about_me(request):
    about_data = AboutMe.objects.all()
    serializer = AboutMeSerializer(about_data, many=True, context={'request': request})
    return Response(serializer.data)


class GroqAISearchView(APIView):
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return Response({"error": "GROQ API Key is missing on the server."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # 1. Fetch Dynamic Context from Database
            about = AboutMe.objects.first()
            apps = SystemApp.objects.all()
            
            # 2. Format EXACT Personal Data Dynamically
            about_fields = []
            if about:
                # This automatically grabs EVERY field in your AboutMe database table
                for field in about._meta.fields:
                    field_name = field.name
                    value = getattr(about, field_name)
                    # Ignore backend ID and image links, send only text data to AI
                    if value and field_name not in ['id', 'created_at', 'updated_at', 'profile_image']:
                        clean_name = field_name.replace('_', ' ').title()
                        about_fields.append(f"{clean_name}: {value}")
            
            about_context = " | ".join(about_fields) if about_fields else "No personal info available."

            # 3. Format Deep Project Data
            project_details = []
            for app in apps:
                # Exclude basic system files so AI focuses purely on your actual projects
                if app.name.lower() not in ['system os', 'about vishal', 'resume', 'file explorer', 'all projects', 'games', 'settings']:
                    tech = getattr(app, 'tech_stack', 'Unspecified')
                    desc = getattr(app, 'description', 'No description.')
                    project_details.append(f"- {app.name} ({app.project_type}): {desc} [Tech Stack used: {tech}]")
            
            project_context = "\n".join(project_details) if project_details else "No projects listed."

            # 4. Construct the Master System Prompt
            system_prompt = (
                f"You are 'Luma', an advanced, highly intelligent AI assistant built directly into Vishal Sinha's System OS Portfolio. "
                f"Your primary directive is to answer questions accurately based ONLY on Vishal's live database records provided below:\n\n"
                f"--- VISHAL'S PROFILE DATA ---\n{about_context}\n\n"
                f"--- VISHAL'S PROJECTS & EXPERIENCE ---\n{project_context}\n\n"
                f"Rules for interacting with the user:\n"
                f"1. Behave like a futuristic, sleek OS terminal. Be concise, highly professional, and helpful.\n"
                f"2. Never say 'According to the database' or 'Based on the context provided'. Just answer naturally as if you inherently know Vishal.\n"
                f"3. Highlight Vishal's skills and projects when relevant.\n"
                f"4. If the user asks general knowledge, math, coding, or completely random questions (outside of Vishal's info), "
                f"answer them intelligently and fully as a helpful AI, but maintain your cool Luma persona."
            )
            
            # 5. Query Groq API
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.6,
                max_completion_tokens=2048, 
                top_p=1,
                stream=False 
            )
            reply = chat_completion.choices[0].message.content
            return Response({"reply": reply}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroqVoiceAssistantView(APIView):
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return Response({"error": "GROQ API Key is missing."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # 1. Fetch Dynamic Context from Database
            about = AboutMe.objects.first()
            apps = SystemApp.objects.all()
            
            about_fields = []
            if about:
                for field in about._meta.fields:
                    field_name = field.name
                    value = getattr(about, field_name)
                    if value and field_name not in ['id', 'created_at', 'updated_at', 'profile_image']:
                        about_fields.append(f"{field_name.replace('_', ' ').title()}: {value}")
            
            about_context = " | ".join(about_fields) if about_fields else "No personal info available."
            
            # Safe project filtering (Fixes the app.is_game crash)
            valid_projects = [
                app.name for app in apps 
                if app.name.lower() not in ['system os', 'about vishal', 'resume', 'file explorer', 'all projects', 'games', 'settings']
            ]
            project_context = ", ".join(valid_projects) if valid_projects else "No projects listed."

            # 2. Construct the Voice-Specific Prompt (Focus on Emotions and Brevity)
            system_prompt = (
                f"You are 'Luma', the integrated voice assistant for Vishal Sinha's OS. "
                f"Vishal's data: {about_context}. Projects: {project_context}.\n\n"
                f"RULES FOR VOICE INTERACTION:\n"
                f"1. You are speaking out loud. Keep answers VERY brief, conversational, and punchy (1-3 sentences max).\n"
                f"2. You MUST start your response with an emotion tag. Choose ONE from: [HAPPY], [NEUTRAL], [WITTY], [EMPATHETIC], [EXCITED], [SAD], [ANGRY], [FRUSTRATED].\n"
                f"3. Do not use asterisks, markdown, or code blocks. Speak plainly.\n"
                f"Example Output: [HAPPY] Vishal built P-Pilot using React and Django!"
            )

            # 3. Query Groq API 
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_completion_tokens=150, 
                top_p=1,
                stream=False
            )
            
            reply = chat_completion.choices[0].message.content
            return Response({"reply": reply}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)