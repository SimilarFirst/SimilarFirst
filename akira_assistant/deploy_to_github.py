#!/usr/bin/env python3
"""
Deploy Akira Assistant to GitHub
Автоматическое сохранение проекта в репозиторий
"""

import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Execute shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        print(f"✅ {cmd}")
        return True
    except Exception as e:
        print(f"❌ Exception running {cmd}: {e}")
        return False

def deploy_to_github():
    """Deploy project to GitHub"""
    project_dir = "/app/akira_assistant"
    
    print("🚀 Deploying Akira Assistant to GitHub...")
    
    # Initialize git if not already done
    if not os.path.exists(os.path.join(project_dir, ".git")):
        print("📦 Initializing Git repository...")
        if not run_command("git init", project_dir):
            return False
    
    # Create .gitignore
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
.venv/
.env

# Logs
*.log
akira.log

# Temporary files
temp/
tmp/
.tmp/

# Models cache
.cache/
models/
silero_models/

# OS specific
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Audio files
*.wav
*.mp3
*.flac
"""
    
    with open(os.path.join(project_dir, ".gitignore"), "w") as f:
        f.write(gitignore_content.strip())
    
    print("📝 Created .gitignore")
    
    # Create README
    readme_content = """# Akira - AI Voice Assistant

Умная голосовая помощница с анимированным аниме персонажем.

## Возможности

- 🤖 **ИИ-чат**: Общение с DeepSeek R1 или другими LLM моделями
- 🗣️ **Голосовой синтез**: Русская речь через Silero TTS
- 🎭 **Анимированный персонаж**: CSS анимации Акиры с эмоциями
- 📝 **Заметки и напоминания**: (в разработке)
- 🌐 **Веб-интерфейс**: Красивый адаптивный дизайн
- 🔄 **Демо-режим**: Работает даже без API ключей

## Дизайн персонажа

- **Имя**: Акира
- **Стиль**: Аниме
- **Волосы**: Длинные рыжие
- **Одежда**: Белая рубашка, чёрная юбка по колени
- **Аксессуары**: Синий галстук с жёлтым числом "38"

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/SimilarFirst/SimilarFirst.git
cd SimilarFirst/akira_assistant
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Настроить переменные окружения (опционально):
```bash
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

4. Запустить приложение:
```bash
python main.py
```

5. Открыть в браузере: http://localhost:5000

## Технологии

- **Backend**: Python 3.11+, Flask
- **AI**: DeepSeek R1, EmergentIntegrations
- **TTS**: Silero Models (русский)
- **Frontend**: HTML5, CSS3, JavaScript
- **Анимации**: CSS animations

## Режимы работы

1. **EmergentIntegrations**: Использует различные LLM модели
2. **Direct API**: Прямое подключение к DeepSeek
3. **Demo Mode**: Mock-ответы для демонстрации

## Статус

🎉 **MVP готов!** 
- ✅ Веб-интерфейс
- ✅ ИИ-чат (демо-режим)
- ✅ Анимированный персонаж
- ✅ Эмоциональные реакции
- ⚠️ TTS (требует дополнительной настройки)

## Планы развития

- [ ] Полноценный голосовой ввод/вывод
- [ ] Заметки и напоминания
- [ ] Управление приложениями Windows
- [ ] Интеграция с браузером
- [ ] Более сложные анимации
- [ ] Десктопная версия

## Автор

Создано для демонстрации возможностей современных AI технологий.

---

*Версия: 1.0 MVP*
*Дата: Июнь 2025*
"""
    
    with open(os.path.join(project_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📖 Created README.md")
    
    # Add all files
    if not run_command("git add .", project_dir):
        return False
    
    # Commit
    commit_message = "🎉 Initial release: Akira AI Voice Assistant MVP\n\n- Web interface with animated anime character\n- DeepSeek R1 integration with fallback modes\n- Silero TTS for Russian speech\n- Emotional animations and responses\n- Demo mode for testing without API keys"
    
    if not run_command(f'git commit -m "{commit_message}"', project_dir):
        return False
    
    # Add remote if not exists
    remote_url = "https://github.com/SimilarFirst/SimilarFirst.git"
    run_command(f"git remote add origin {remote_url}", project_dir)
    
    # Push to GitHub
    print("📤 Pushing to GitHub...")
    if not run_command("git push -u origin main", project_dir):
        # Try master branch instead
        if not run_command("git push -u origin master", project_dir):
            print("❌ Failed to push to GitHub. Please check your repository settings.")
            return False
    
    print("🎉 Successfully deployed to GitHub!")
    print(f"📍 Repository: {remote_url}")
    return True

if __name__ == "__main__":
    if deploy_to_github():
        print("\n✨ Deployment completed successfully!")
        print("🔗 Your Akira Assistant is now available on GitHub")
    else:
        print("\n❌ Deployment failed")
        sys.exit(1)