#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de ejemplo para ISTEM
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# Add the backend directory to the path
sys.path.append('/app/backend')

# MongoDB connection
mongo_url = "mongodb://localhost:27017"
client = AsyncIOMotorClient(mongo_url)
db = client["test_database"]

# Sample data
SAMPLE_COURSES = [
    {
        "id": "course-python-basics",
        "title": "Fundamentos de Python",
        "description": "Aprende los fundamentos de Python desde cero. Ideal para principiantes que quieren iniciarse en el mundo de la programación.",
        "instructor_id": "instructor-maria",
        "instructor_name": "María García",
        "thumbnail": "https://images.unsplash.com/photo-1526379879527-8559ecfcaec0?ixlib=rb-4.1.0&auto=format&fit=crop&w=800&q=80",
        "duration_hours": 40,
        "level": "Beginner",
        "price": 0.0,
        "is_published": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "course-web-development",
        "title": "Desarrollo Web Moderno",
        "description": "Domina HTML, CSS, JavaScript y React. Construye aplicaciones web modernas y responsivas desde cero.",
        "instructor_id": "instructor-carlos",
        "instructor_name": "Carlos Rodríguez",
        "thumbnail": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.1.0&auto=format&fit=crop&w=800&q=80",
        "duration_hours": 60,
        "level": "Intermediate",
        "price": 99.0,
        "is_published": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "course-data-science",
        "title": "Ciencia de Datos con Python",
        "description": "Explora el mundo de la ciencia de datos. Aprende pandas, numpy, matplotlib y técnicas de machine learning.",
        "instructor_id": "instructor-ana",
        "instructor_name": "Ana Martínez",
        "thumbnail": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.1.0&auto=format&fit=crop&w=800&q=80",
        "duration_hours": 80,
        "level": "Advanced",
        "price": 149.0,
        "is_published": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "course-mobile-dev",
        "title": "Desarrollo de Apps Móviles",
        "description": "Crea aplicaciones móviles nativas usando React Native. Publica en App Store y Google Play.",
        "instructor_id": "instructor-luis",
        "instructor_name": "Luis Fernández",
        "thumbnail": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?ixlib=rb-4.1.0&auto=format&fit=crop&w=800&q=80",
        "duration_hours": 50,
        "level": "Intermediate",
        "price": 79.0,
        "is_published": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "course-ai-fundamentals",
        "title": "Fundamentos de Inteligencia Artificial",
        "description": "Introducción a la IA moderna. Aprende sobre machine learning, neural networks y aplicaciones prácticas.",
        "instructor_id": "instructor-sofia",
        "instructor_name": "Sofia López",
        "thumbnail": "https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-4.1.0&auto=format&fit=crop&w=800&q=80",
        "duration_hours": 45,
        "level": "Intermediate",
        "price": 129.0,
        "is_published": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

SAMPLE_LESSONS = [
    # Python Basics Course Lessons
    {
        "id": "lesson-python-1",
        "course_id": "course-python-basics",
        "title": "Introducción a Python",
        "description": "Qué es Python y por qué es tan popular",
        "content": "En esta lección aprenderás los conceptos básicos de Python, su historia y por qué es el lenguaje de programación más popular del mundo.",
        "lesson_type": "video",
        "duration_minutes": 30,
        "order": 1,
        "created_at": datetime.utcnow()
    },
    {
        "id": "lesson-python-2",
        "course_id": "course-python-basics",
        "title": "Variables y Tipos de Datos",
        "description": "Aprende a trabajar con variables y diferentes tipos de datos",
        "content": "Exploraremos strings, números, listas, diccionarios y otros tipos de datos fundamentales en Python.",
        "lesson_type": "video",
        "duration_minutes": 45,
        "order": 2,
        "created_at": datetime.utcnow()
    },
    {
        "id": "lesson-python-3",
        "course_id": "course-python-basics",
        "title": "Control de Flujo",
        "description": "Condicionales y bucles en Python",
        "content": "Aprende a usar if/else, for y while para controlar el flujo de tu programa.",
        "lesson_type": "video",
        "duration_minutes": 40,
        "order": 3,
        "created_at": datetime.utcnow()
    },
    # Web Development Course Lessons
    {
        "id": "lesson-web-1",
        "course_id": "course-web-development",
        "title": "HTML5 Fundamentals",
        "description": "Estructura básica de páginas web con HTML5",
        "content": "Aprende la estructura semántica de HTML5 y las mejores prácticas para crear páginas web modernas.",
        "lesson_type": "video",
        "duration_minutes": 50,
        "order": 1,
        "created_at": datetime.utcnow()
    },
    {
        "id": "lesson-web-2",
        "course_id": "course-web-development",
        "title": "CSS3 y Diseño Responsivo",
        "description": "Estilos modernos y diseño adaptativo",
        "content": "Domina CSS3, Flexbox, Grid y técnicas de diseño responsivo para crear interfaces atractivas.",
        "lesson_type": "video",
        "duration_minutes": 60,
        "order": 2,
        "created_at": datetime.utcnow()
    }
]

SAMPLE_MEETINGS = [
    {
        "id": "meeting-python-q&a",
        "course_id": "course-python-basics",
        "title": "Sesión Q&A - Python Basics",
        "description": "Resolvemos dudas sobre los fundamentos de Python",
        "scheduled_at": datetime.utcnow() + timedelta(days=2, hours=3),
        "duration_minutes": 60,
        "meeting_url": "https://meet.google.com/sample-python-qa",
        "instructor_id": "instructor-maria",
        "max_participants": 50,
        "created_at": datetime.utcnow()
    },
    {
        "id": "meeting-web-workshop",
        "course_id": "course-web-development",
        "title": "Workshop: Proyecto React",
        "description": "Construyamos una app React juntos paso a paso",
        "scheduled_at": datetime.utcnow() + timedelta(days=5, hours=2),
        "duration_minutes": 90,
        "meeting_url": "https://meet.google.com/sample-react-workshop",
        "instructor_id": "instructor-carlos",
        "max_participants": 30,
        "created_at": datetime.utcnow()
    },
    {
        "id": "meeting-data-science-intro",
        "course_id": "course-data-science",
        "title": "Introducción a Machine Learning",
        "description": "Conceptos básicos de ML y casos de uso reales",
        "scheduled_at": datetime.utcnow() + timedelta(days=7, hours=4),
        "duration_minutes": 75,
        "meeting_url": "https://meet.google.com/sample-ml-intro",
        "instructor_id": "instructor-ana",
        "max_participants": 40,
        "created_at": datetime.utcnow()
    }
]

async def populate_database():
    """Poblar la base de datos con datos de ejemplo"""
    try:
        print("🚀 Iniciando población de datos para ISTEM...")
        
        # Clear existing data
        await db.courses.delete_many({})
        await db.lessons.delete_many({})
        await db.meetings.delete_many({})
        print("✅ Datos existentes limpiados")
        
        # Insert courses
        await db.courses.insert_many(SAMPLE_COURSES)
        print(f"✅ {len(SAMPLE_COURSES)} cursos insertados")
        
        # Insert lessons
        await db.lessons.insert_many(SAMPLE_LESSONS)
        print(f"✅ {len(SAMPLE_LESSONS)} lecciones insertadas")
        
        # Insert meetings
        await db.meetings.insert_many(SAMPLE_MEETINGS)
        print(f"✅ {len(SAMPLE_MEETINGS)} reuniones insertadas")
        
        print("\n🎉 ¡Base de datos poblada exitosamente!")
        print("📚 Cursos disponibles:")
        for course in SAMPLE_COURSES:
            print(f"   - {course['title']} ({course['level']}) - {course['instructor_name']}")
        
        print("\n📅 Próximas reuniones:")
        for meeting in SAMPLE_MEETINGS:
            print(f"   - {meeting['title']} - {meeting['scheduled_at'].strftime('%Y-%m-%d %H:%M')}")
            
    except Exception as e:
        print(f"❌ Error poblando la base de datos: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(populate_database())