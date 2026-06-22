"""
setup_demo.py — Wypelnia baze danych przykladowymi danymi prezentacyjnymi.
Usuwa WSZYSTKIE istniejace dane i tworzy kompletny zestaw kont, kursow,
materialow, quizow, zapisow i postepu.

Uzycie: python manage.py setup_demo
"""
import os
import uuid
import hashlib
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from cryptography.fernet import Fernet


def _f():
    return Fernet(os.getenv('ENCRYPTION_KEY').encode())


def enc(text):
    return _f().encrypt(text.encode()).decode()


def sha3(text):
    return hashlib.sha3_256(text.strip().lower().encode()).hexdigest()


def uid():
    return str(uuid.uuid4())


def ago(days, hours=0):
    return datetime.datetime.utcnow() - datetime.timedelta(days=days, hours=hours)


class Command(BaseCommand):
    help = 'Czyści całą bazę i wstawia dane demo do prezentacji portalu DJIC'

    def handle(self, *args, **options):
        from users.models import MongoUser
        from courses.models import Course, Material
        from quizzes.models import Quiz, QuizQuestion, QuizOption, QuizResult
        from progress.models import Enrollment, Progress, Achievement, BADGE_CATALOGUE
        from notifications.models import Notification
        from admin_panel.models import SystemLog, SystemSettings

        w = self.stdout.write
        ok = self.style.SUCCESS
        hi = self.style.WARNING

        # ======================================================================
        # 1. CZYSZCZENIE BAZY
        # ======================================================================
        w(hi('>>> Czyszczenie calej bazy danych...'))
        Notification.objects.all().delete()
        Achievement.objects.all().delete()
        Progress.objects.all().delete()
        Enrollment.objects.all().delete()
        QuizResult.objects.all().delete()
        Quiz.objects.all().delete()
        Material.objects.all().delete()
        Course.objects.all().delete()
        MongoUser.objects.all().delete()
        SystemLog.objects.all().delete()
        w(ok('  [OK] Baza wyczyszczona.'))

        # ══════════════════════════════════════════════════════════════════════
        # 2. UŻYTKOWNICY
        # ══════════════════════════════════════════════════════════════════════
        w(hi('>>> Tworzenie uzytkownikow...'))

        def make_user(email, password, name, role, bio='', days_ago=30):
            u = MongoUser(
                email=enc(email),
                email_hash=sha3(email),
                password=make_password(password),
                name=enc(name),
                bio=bio,
                role=role,
                is_verified=True,
                is_active=True,
                created_at=ago(days_ago),
                last_login=ago(days_ago // 3),
            )
            u.save()
            return u

        # ── Admin ──────────────────────────────────────────────────────────
        admin = make_user(
            'admin@djic.pl', 'Admin@djic2024', 'Administrator DJIC', 'ADMIN',
            bio='Główny administrator platformy DJIC.', days_ago=120,
        )

        # ── Kreatorzy ─────────────────────────────────────────────────────
        anna = make_user(
            'anna.kowalska@djic.pl', 'Haslo@2024', 'Anna Kowalska', 'CREATOR',
            bio='Specjalistka frontend i UX/UI. 8 lat doświadczenia w Vue.js i React.',
            days_ago=90,
        )
        marek = make_user(
            'marek.nowak@djic.pl', 'Haslo@2024', 'Marek Nowak', 'CREATOR',
            bio='Senior backend developer. Ekspert Django, PostgreSQL i Node.js.',
            days_ago=85,
        )
        piotr = make_user(
            'piotr.wisniewski@djic.pl', 'Haslo@2024', 'Piotr Wiśniewski', 'CREATOR',
            bio='DevOps engineer i specjalista cyberbezpieczeństwa. Certyfikowany AWS i Kubernetes.',
            days_ago=80,
        )
        julia = make_user(
            'julia.kaminska@djic.pl', 'Haslo@2024', 'Julia Kamińska', 'CREATOR',
            bio='Data scientist i mobile developer. Autorka kursów z ML i Fluttera.',
            days_ago=75,
        )

        # ── Studenci ──────────────────────────────────────────────────────
        s1  = make_user('jan.malinowski@djic.pl',    'Haslo@2024', 'Jan Malinowski',    'STUDENT', days_ago=60)
        s2  = make_user('monika.zajac@djic.pl',      'Haslo@2024', 'Monika Zając',      'STUDENT', days_ago=55)
        s3  = make_user('tomasz.kowalski@djic.pl',   'Haslo@2024', 'Tomasz Kowalski',   'STUDENT', days_ago=50)
        s4  = make_user('karolina.lis@djic.pl',      'Haslo@2024', 'Karolina Lis',      'STUDENT', days_ago=48)
        s5  = make_user('adam.wierzbicki@djic.pl',   'Haslo@2024', 'Adam Wierzbicki',   'STUDENT', days_ago=45)
        s6  = make_user('natalia.dabrowska@djic.pl', 'Haslo@2024', 'Natalia Dąbrowska', 'STUDENT', days_ago=40)
        s7  = make_user('michal.szymanski@djic.pl',  'Haslo@2024', 'Michał Szymański',  'STUDENT', days_ago=35)
        s8  = make_user('aleksandra.wojcik@djic.pl', 'Haslo@2024', 'Aleksandra Wójcik', 'STUDENT', days_ago=30)
        s9  = make_user('pawel.nowak@djic.pl',       'Haslo@2024', 'Paweł Nowak',       'STUDENT', days_ago=25)
        s10 = make_user('zofia.kaminska@djic.pl',    'Haslo@2024', 'Zofia Kamińska',    'STUDENT', days_ago=20)

        w(ok('  [OK] Utworzono 15 uzytkownikow (1 admin, 4 kreatorow, 10 studentow).'))

        # ══════════════════════════════════════════════════════════════════════
        # 3. KURSY + MATERIAŁY + QUIZY
        # ══════════════════════════════════════════════════════════════════════
        w(hi('>>> Tworzenie kursow, materialow i quizow...'))

        def make_course(creator, title, description, category, level, tags,
                        duration, status='ACTIVE', days_ago=60, reject_reason=''):
            c = Course(
                title=title,
                description=description,
                category=category,
                level=level,
                tags=tags,
                creator_id=str(creator.id),
                price=0,
                duration_minutes=duration,
                status=status,
                created_at=ago(days_ago),
                updated_at=ago(days_ago - 2),
                published_at=ago(days_ago - 5) if status == 'ACTIVE' else None,
                reject_reason=reject_reason,
            )
            c.save()
            return c

        def make_material(course, title, mtype, content, order, duration_seconds=0):
            m = Material(
                course_id=str(course.id),
                title=title,
                type=mtype,
                content=content,
                order=order,
                duration_seconds=duration_seconds,
                created_at=ago(55),
            )
            m.save()
            return m

        def make_quiz(course, material, title, questions_data):
            """questions_data: list of (text, [options_text], correct_index)"""
            questions = []
            for q_text, opts, correct_idx in questions_data:
                options = [QuizOption(id=uid(), text=o) for o in opts]
                questions.append(QuizQuestion(
                    id=uid(),
                    text=q_text,
                    options=options,
                    correct_option_id=options[correct_idx].id,
                    points=1,
                ))
            quiz = Quiz(
                course_id=str(course.id),
                material_id=str(material.id),
                title=title,
                time_limit_seconds=300,
                questions=questions,
                created_at=ago(54),
            )
            quiz.save()
            # Aktualizuj content materiału na quiz_id
            material.content = str(quiz.id)
            material.save()
            return quiz

        TEXT_VUE = """<h2>Podstawy Vue 3</h2>
<p>Vue 3 wprowadza <strong>Composition API</strong> jako alternatywę dla Options API.
Pozwala na lepszą organizację logiki komponentu i ponowne użycie kodu.</p>
<h3>Kluczowe koncepcje</h3>
<ul>
  <li><code>ref()</code> — reaktywna zmienna prymitywna</li>
  <li><code>reactive()</code> — reaktywny obiekt</li>
  <li><code>computed()</code> — właściwość obliczana</li>
  <li><code>watch()</code> — obserwowanie zmian</li>
  <li><code>onMounted()</code> — hook cyklu życia</li>
</ul>
<pre><code>import { ref, computed } from 'vue'
const count = ref(0)
const double = computed(() => count.value * 2)
</code></pre>"""

        TEXT_CSS = """<h2>Flexbox i CSS Grid</h2>
<p>Dwa najpotężniejsze systemy layoutu w CSS:</p>
<h3>Flexbox — jednowymiarowy</h3>
<pre><code>.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}</code></pre>
<h3>CSS Grid — dwuwymiarowy</h3>
<pre><code>.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}</code></pre>"""

        TEXT_TS = """<h2>TypeScript — Typowanie Statyczne</h2>
<p>TypeScript dodaje statyczne typowanie do JavaScriptu, co eliminuje wiele błędów w fazie kompilacji.</p>
<h3>Interfejsy i Typy</h3>
<pre><code>interface User {
  id: number
  name: string
  email?: string  // opcjonalne
}

type Role = 'ADMIN' | 'CREATOR' | 'STUDENT'

function greet(user: User): string {
  return `Czesc, ${user.name}!`
}</code></pre>"""

        TEXT_UX = """<h2>Podstawy UX/UI Design</h2>
<p>Dobry design to połączenie estetyki i użyteczności. Kluczowe zasady:</p>
<ul>
  <li><strong>Hierarchia wizualna</strong> — kieruj wzrok użytkownika</li>
  <li><strong>Kontrast</strong> — zapewnia czytelność</li>
  <li><strong>Spójność</strong> — jeden język wizualny przez cały produkt</li>
  <li><strong>Feedback</strong> — użytkownik musi wiedzieć, co się dzieje</li>
</ul>
<h3>Zasady Gestalt</h3>
<p>Bliskość, podobieństwo, kontynuacja, domknięcie — mózg automatycznie grupuje elementy.</p>"""

        TEXT_DRF = """<h2>Django REST Framework</h2>
<p>DRF to najpopularniejsza biblioteka do budowania API w Pythonie.</p>
<h3>Serializatory</h3>
<pre><code>class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'created_at']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Tytuł za krótki.')
        return value</code></pre>
<h3>ViewSets</h3>
<p>ViewSet łączy wszystkie operacje CRUD w jednej klasie, minimalizując powtarzalność kodu.</p>"""

        TEXT_PSQL = """<h2>Optymalizacja PostgreSQL</h2>
<p>Wydajne zapytania SQL to kluczowa kompetencja każdego backend dewelopera.</p>
<h3>EXPLAIN ANALYZE</h3>
<pre><code>EXPLAIN ANALYZE
SELECT u.name, COUNT(e.id) as enrollments
FROM users u
LEFT JOIN enrollments e ON u.id = e.user_id
GROUP BY u.id, u.name
ORDER BY enrollments DESC;</code></pre>
<h3>Indeksy</h3>
<p>Indeks złożony na często filtrowanych polach może zmniejszyć czas zapytania 100-krotnie.</p>"""

        TEXT_NODE = """<h2>Node.js i Express</h2>
<p>Node.js to środowisko uruchomieniowe JS na serwerze oparte na silniku V8.</p>
<h3>Middleware</h3>
<pre><code>const express = require('express')
const app = express()

app.use(express.json())

app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`)
  next()
})

app.get('/api/users', async (req, res) => {
  const users = await User.find()
  res.json(users)
})</code></pre>"""

        TEXT_MONGO = """<h2>MongoDB — Bazy NoSQL</h2>
<p>MongoDB przechowuje dane w dokumentach BSON (podobnych do JSON), bez sztywnego schematu.</p>
<h3>Agregacje</h3>
<pre><code>db.courses.aggregate([
  { $match: { status: 'ACTIVE' } },
  { $group: {
    _id: '$category',
    count: { $sum: 1 },
    avgDuration: { $avg: '$duration_minutes' }
  }},
  { $sort: { count: -1 } }
])</code></pre>"""

        TEXT_DOCKER = """<h2>Docker i Kubernetes</h2>
<p>Konteneryzacja rozwiązuje problem „u mnie działa" — aplikacja jest spakowana ze wszystkimi zależnościami.</p>
<h3>Dockerfile</h3>
<pre><code>FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]</code></pre>
<h3>docker-compose.yml</h3>
<pre><code>services:
  web:
    build: .
    ports: ["8000:8000"]
  db:
    image: mongo:7</code></pre>"""

        TEXT_HACK = """<h2>Podstawy Cyberbezpieczeństwa</h2>
<p>Ethical hacking to legalne testowanie systemów w celu wykrycia podatności przed złośliwymi aktorami.</p>
<h3>Najczęstsze podatności (OWASP Top 10)</h3>
<ul>
  <li>SQL Injection</li>
  <li>Cross-Site Scripting (XSS)</li>
  <li>Broken Access Control</li>
  <li>Insecure Deserialization</li>
  <li>Security Misconfiguration</li>
</ul>
<p><strong>Pamiętaj:</strong> testowanie bez autoryzacji jest nielegalne. Zawsze działaj w ramach umowy lub własnego środowiska.</p>"""

        TEXT_CICD = """<h2>CI/CD — Automatyzacja Wdrożeń</h2>
<p>CI/CD eliminuje ręczne procesy: każdy commit automatycznie przechodzi przez testy i deployment.</p>
<h3>GitHub Actions — przykład</h3>
<pre><code>name: CI Pipeline
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - run: pytest --tb=short</code></pre>"""

        TEXT_LINUX = """<h2>Linux — Administracja Systemu</h2>
<p>Linux to podstawa każdej infrastruktury serwerowej. Znajomość CLI jest obowiązkowa dla każdego dewelopera.</p>
<h3>Najważniejsze polecenia</h3>
<pre><code># Uprawnienia
chmod 755 script.sh && chown www-data:www-data /var/www

# Monitoring procesów
htop
ps aux | grep python

# Cron — zadania cykliczne
crontab -e
# 0 2 * * * /backup.sh  ← codziennie o 2:00</code></pre>"""

        TEXT_PYDS = """<h2>Python dla Analizy Danych</h2>
<p>Pandas i NumPy to fundament każdego projektu data science w Pythonie.</p>
<h3>Wczytanie i eksploracja danych</h3>
<pre><code>import pandas as pd
import numpy as np

df = pd.read_csv('dane.csv')
print(df.head())
print(df.describe())
print(df.isnull().sum())

# Grupowanie
df.groupby('kategoria')['wartość'].mean()</code></pre>"""

        TEXT_ML = """<h2>Machine Learning z scikit-learn</h2>
<p>scikit-learn to najdojrzalsza biblioteka ML w Pythonie — prosta API, bogate algorytmy.</p>
<h3>Klasyczny pipeline ML</h3>
<pre><code>from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(n_estimators=100)),
])

scores = cross_val_score(pipe, X_train, y_train, cv=5)
print(f'CV Accuracy: {scores.mean():.3f} ± {scores.std():.3f}')</code></pre>"""

        TEXT_FLUTTER = """<h2>Flutter — Wieloplatformowe Aplikacje</h2>
<p>Flutter pozwala budować aplikacje iOS, Android, web i desktop z jednej bazy kodu w Dart.</p>
<h3>Podstawowy Widget</h3>
<pre><code>class MyButton extends StatefulWidget {
  @override
  State<MyButton> createState() => _MyButtonState();
}

class _MyButtonState extends State<MyButton> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () => setState(() => _count++),
      child: Text('Kliknięto: $_count'),
    );
  }
}</code></pre>"""

        # ── Definicje kursów ──────────────────────────────────────────────

        COURSES = [
            # (creator, title, desc, category, level, tags, duration, status, text_content)
            (anna, 'Vue.js 3 — Kompletny Przewodnik',
             'Opanuj Vue 3 z Composition API, Pinia, Vue Router i TypeScript. Kurs od podstaw do zaawansowanego.',
             'Frontend', 'INTERMEDIATE', ['vue', 'javascript', 'spa'], 1200, 'ACTIVE', TEXT_VUE),

            (anna, 'CSS Grid i Flexbox — Mistrzostwo Layoutu',
             'Naucz się budować nowoczesne, responsywne layouty CSS bez zewnętrznych frameworków.',
             'Frontend', 'BEGINNER', ['css', 'flexbox', 'grid', 'responsive'], 360, 'ACTIVE', TEXT_CSS),

            (anna, 'TypeScript od Podstaw do Zaawansowanego',
             'Statyczne typowanie, interfejsy, generyki, dekoratory — wszystko czego potrzebujesz w TypeScript.',
             'Frontend', 'INTERMEDIATE', ['typescript', 'javascript', 'typy'], 480, 'ACTIVE', TEXT_TS),

            (anna, 'Projektowanie UX/UI dla Programistów',
             'Naucz się zasad projektowania interfejsów użytkownika, Figma i podstaw psychologii użytkownika.',
             'UI/UX', 'BEGINNER', ['ux', 'ui', 'figma', 'design'], 600, 'ACTIVE', TEXT_UX),

            (marek, 'Django REST Framework — API od A do Z',
             'Buduj skalowalne REST API w Pythonie. Serializatory, ViewSets, uwierzytelnianie JWT i wiele więcej.',
             'Backend', 'ADVANCED', ['django', 'python', 'api', 'rest'], 900, 'ACTIVE', TEXT_DRF),

            (marek, 'PostgreSQL — Optymalizacja Zapytań',
             'Zaawansowane techniki optymalizacji: indeksy, EXPLAIN ANALYZE, partycjonowanie, CTE i okna agregacji.',
             'Bazy danych', 'INTERMEDIATE', ['postgresql', 'sql', 'bazy danych'], 720, 'ACTIVE', TEXT_PSQL),

            (marek, 'Node.js i Express — Nowoczesne API',
             'Twórz wydajne API REST i GraphQL w Node.js z Express, Prisma i testami Supertest.',
             'Backend', 'INTERMEDIATE', ['nodejs', 'express', 'javascript'], 540, 'ACTIVE', TEXT_NODE),

            (marek, 'MongoDB — Bazy NoSQL w Praktyce',
             'Dokumentowe bazy danych: ModelEngine, agregacje, indeksy i strategie skalowania dla dużych zbiorów.',
             'Bazy danych', 'BEGINNER', ['mongodb', 'nosql', 'bazy danych'], 420, 'ACTIVE', TEXT_MONGO),

            (piotr, 'Docker i Kubernetes — Konteneryzacja Aplikacji',
             'Konteneryzacja od Dockerfile przez docker-compose do orkiestracji klastra Kubernetes w chmurze.',
             'DevOps', 'INTERMEDIATE', ['docker', 'kubernetes', 'devops', 'kontenery'], 660, 'ACTIVE', TEXT_DOCKER),

            (piotr, 'Ethical Hacking — Podstawy Cyberbezpieczeństwa',
             'Ucz się myśleć jak haker, aby lepiej bronić systemy. Zakres: OWASP, recon, exploitacja, raportowanie.',
             'Bezpieczeństwo', 'ADVANCED', ['security', 'hacking', 'owasp', 'pentesting'], 780, 'ACTIVE', TEXT_HACK),

            (piotr, 'CI/CD z GitHub Actions i GitLab',
             'Automatyzuj budowanie, testowanie i wdrażanie aplikacji. Od podstaw do zaawansowanych pipeline\'ów.',
             'DevOps', 'BEGINNER', ['cicd', 'github', 'gitlab', 'devops'], 300, 'ACTIVE', TEXT_CICD),

            (piotr, 'Linux — Administracja i Skrypty Bash',
             'Opanuj wiersz poleceń Linux, zarządzanie procesami, uprawnieniami, siecią i automatyzację Bash.',
             'DevOps', 'INTERMEDIATE', ['linux', 'bash', 'cli', 'admin'], 480, 'ACTIVE', TEXT_LINUX),

            (julia, 'Python dla Analityków Danych',
             'Pandas, NumPy, Matplotlib i Seaborn — kompletne wprowadzenie do ekosystemu data science w Pythonie.',
             'Data Science', 'BEGINNER', ['python', 'pandas', 'data science'], 540, 'ACTIVE', TEXT_PYDS),

            (julia, 'Machine Learning z scikit-learn',
             'Nadzorowane i nienadzorowane uczenie maszynowe: regresja, klasyfikacja, clustering, cross-walidacja.',
             'Data Science', 'INTERMEDIATE', ['ml', 'python', 'scikit-learn', 'ai'], 720, 'ACTIVE', TEXT_ML),

            (julia, 'Flutter — Wieloplatformowe Aplikacje',
             'Buduj aplikacje iOS, Android i web z jednej bazy kodu. Dart, Widgety, State Management, nawigacja.',
             'Mobile', 'INTERMEDIATE', ['flutter', 'dart', 'mobile', 'crossplatform'], 600, 'ACTIVE', TEXT_FLUTTER),

            # REVIEW — oczekuje na zatwierdzenie
            (julia, 'Android z Kotlin — Kurs Kompletny',
             'Natywne aplikacje Android z Kotlin, Jetpack Compose, Room i ViewModel.',
             'Mobile', 'ADVANCED', ['android', 'kotlin', 'mobile'], 840, 'REVIEW', TEXT_FLUTTER),

            # DRAFT — w trakcie tworzenia
            (anna, 'React 18 i Next.js — Od Podstaw',
             'Nowoczesny frontend z React Hooks, Server Components, App Router i Tailwind CSS.',
             'Frontend', 'INTERMEDIATE', ['react', 'nextjs', 'javascript'], 720, 'DRAFT', TEXT_VUE),
        ]

        QUIZ_DATA = {
            'Vue.js 3 — Kompletny Przewodnik': [
                ('Czym jest Composition API w Vue 3?',
                 ['Alternatywą dla Options API umożliwiającą lepszą organizację logiki', 'Biblioteką komponentów UI', 'Systemem routingu', 'Narzędziem CLI'], 0),
                ('Która funkcja tworzy reaktywną zmienną prymitywną?',
                 ['ref()', 'reactive()', 'state()', 'var()'], 0),
                ('Do czego służy computed() w Vue?',
                 ['Tworzy właściwość obliczaną na podstawie reaktywnych zależności', 'Wykonuje zapytanie HTTP', 'Renderuje komponent warunkowo', 'Definiuje hook'], 0),
                ('Jak działa v-model w Vue 3?',
                 ['Dwukierunkowe wiązanie danych między komponentem a zmienną', 'Renderuje listę elementów', 'Warunkowe ukrywanie elementu', 'Nasłuchuje zdarzeń klawiatury'], 0),
            ],
            'CSS Grid i Flexbox — Mistrzostwo Layoutu': [
                ('Jaką wartość display należy ustawić, aby włączyć Flexbox?',
                 ['flex', 'grid', 'block', 'table'], 0),
                ('Która właściwość wyrównuje elementy Flexbox na osi głównej?',
                 ['justify-content', 'align-items', 'flex-direction', 'order'], 0),
                ('Czym CSS Grid różni się od Flexbox?',
                 ['Grid jest dwuwymiarowy (wiersze i kolumny), Flexbox jednowymiarowy', 'Grid działa tylko w Chrome', 'Flexbox jest nowszy', 'Brak różnic'], 0),
                ('Co robi właściwość flex-grow?',
                 ['Określa jak element rozciąga się względem rodzeństwa', 'Ustawia rozmiar fontu', 'Zmienia kolor tła', 'Dodaje cień'], 0),
            ],
            'TypeScript od Podstaw do Zaawansowanego': [
                ('Co to jest interfejs w TypeScript?',
                 ['Kontrakt opisujący kształt obiektu', 'Klasa abstrakcyjna', 'Moduł ES6', 'Dekorator'], 0),
                ('Jak oznaczyć pole jako opcjonalne w interfejsie?',
                 ['Dodając ? po nazwie pola', 'Dodając ! po nazwie pola', 'Używając Optional<T>', 'Prefiksem maybe:'], 0),
                ('Do czego służą generyki (ang. generics)?',
                 ['Tworzenia wielokrotnie używalnego kodu działającego z różnymi typami', 'Importowania modułów', 'Definiowania stałych', 'Obsługi błędów'], 0),
                ('Czym różni się type od interface?',
                 ['Type może definiować typy unii i przecięcia, interface nie', 'Interface jest szybszy w kompilacji', 'Brak różnic', 'Type jest przestarzały'], 0),
            ],
            'Projektowanie UX/UI dla Programistów': [
                ('Co to jest User Persona?',
                 ['Fikcyjny profil reprezentujący grupę docelowych użytkowników', 'Grafika interfejsu aplikacji', 'Test A/B', 'Szkielet strony'], 0),
                ('Co oznacza skrót UX?',
                 ['User Experience — doświadczenie użytkownika', 'User Execution', 'UI Extended', 'Unique Export'], 0),
                ('Czym jest wireframe?',
                 ['Szkicem struktury interfejsu bez elementów graficznych', 'Finalnym projektem graficznym', 'Kodem HTML strony', 'Raportem z badań użytkownika'], 0),
                ('Która zasada Gestalt mówi, że elementy blisko siebie są postrzegane jako grupa?',
                 ['Zasada bliskości', 'Zasada podobieństwa', 'Zasada kontynuacji', 'Zasada domknięcia'], 0),
            ],
            'Django REST Framework — API od A do Z': [
                ('Co to jest ViewSet w DRF?',
                 ['Klasa łącząca operacje CRUD (list, create, retrieve, update, destroy)', 'Middleware HTTP', 'Serializator danych', 'System cache'], 0),
                ('Jaką metodą serializatora walidujemy dane?',
                 ['is_valid()', 'validate()', 'check()', 'verify()'], 0),
                ('Co robi dekorator @action w ViewSet?',
                 ['Definiuje niestandardowe endpointy poza CRUD', 'Dodaje middleware', 'Konfiguruje CORS', 'Wstrzykuje zależności'], 0),
                ('Który klasa DRF implementuje JWT Authentication?',
                 ['JWTAuthentication (z djangorestframework-simplejwt)', 'TokenAuthentication', 'SessionAuthentication', 'BasicAuthentication'], 0),
            ],
            'PostgreSQL — Optymalizacja Zapytań': [
                ('Do czego służy polecenie EXPLAIN ANALYZE?',
                 ['Pokazuje plan wykonania zapytania z realnymi statystykami', 'Tworzy indeks automatycznie', 'Optymalizuje zapytanie', 'Wyświetla schemat tabeli'], 0),
                ('Czym jest indeks złożony?',
                 ['Indeksem obejmującym wiele kolumn jednocześnie', 'Zagnieżdżonym indeksem', 'Indeksem pełnotekstowym', 'Widokiem bazodanowym'], 0),
                ('Do czego służy CTE (Common Table Expression)?',
                 ['Tworzenia tymczasowego nazwanego podzapytania w ramach jednego SELECT', 'Tworzenia trwałej tabeli', 'Definiowania procedury', 'Zarządzania transakcją'], 0),
                ('Co robi VACUUM w PostgreSQL?',
                 ['Odzyskuje miejsce po usuniętych i zaktualizowanych wierszach', 'Backupuje bazę danych', 'Tworzy kopię tabeli', 'Resetuje sekwencje'], 0),
            ],
            'Node.js i Express — Nowoczesne API': [
                ('Co to jest middleware w Express.js?',
                 ['Funkcja pośrednicząca wykonywana między żądaniem a odpowiedzią', 'Model bazy danych', 'Typ trasy', 'System cache'], 0),
                ('Co robi async/await w Node.js?',
                 ['Obsługuje operacje asynchroniczne w czytelny, synchroniczny sposób', 'Tworzy wątki systemowe', 'Zarządza pamięcią', 'Kompiluje TypeScript'], 0),
                ('Czym jest event loop w Node.js?',
                 ['Mechanizmem umożliwiającym nieblokujące operacje I/O', 'Pętlą for-each', 'Systemem plików', 'Protokołem WebSocket'], 0),
                ('Do czego służy process.env?',
                 ['Odczytu zmiennych środowiskowych', 'Listowania procesów', 'Zarządzania sesjami', 'Kompresji odpowiedzi'], 0),
            ],
            'MongoDB — Bazy NoSQL w Praktyce': [
                ('Czym jest dokument w MongoDB?',
                 ['Rekordem danych w formacie BSON (podobnym do JSON)', 'Tabelą relacyjną', 'Widokiem bazodanowym', 'Procedurą składowaną'], 0),
                ('Która etap agregacji grupuje dokumenty?',
                 ['$group', '$match', '$project', '$sort'], 0),
                ('Czym różni się MongoDB od baz relacyjnych?',
                 ['Brak sztywnego schematu, dokumenty zamiast wierszy w tabelach', 'Jest zawsze szybszy', 'Nie obsługuje indeksów', 'Działa tylko lokalnie'], 0),
                ('Do czego służy operator $lookup?',
                 ['Łączy dokumenty z dwóch kolekcji (odpowiednik JOIN)', 'Wyszukuje tekst', 'Tworzy indeks', 'Usuwa pola'], 0),
            ],
            'Docker i Kubernetes — Konteneryzacja Aplikacji': [
                ('Czym różni się kontener od maszyny wirtualnej?',
                 ['Kontener współdzieli jądro systemu i jest znacznie lżejszy', 'Kontener ma własny system operacyjny', 'Brak różnic', 'Maszyna wirtualna jest szybsza'], 0),
                ('Do czego służy Dockerfile?',
                 ['Instrukcji budowania obrazu Docker krok po kroku', 'Pliku konfiguracyjnego klastra', 'Definicji sieci', 'Wolumenu danych'], 0),
                ('Co to jest Pod w Kubernetes?',
                 ['Najmniejsza jednostka wdrożenia — może zawierać jeden lub więcej kontenerów', 'Węzłem klastra', 'Usługą sieciową', 'Przestrzenią nazw'], 0),
                ('Do czego służy docker-compose?',
                 ['Definiowania i uruchamiania aplikacji składających się z wielu kontenerów', 'Budowania obrazów produkcyjnych', 'Monitorowania logów', 'Zarządzania Registry'], 0),
            ],
            'Ethical Hacking — Podstawy Cyberbezpieczeństwa': [
                ('Co to jest penetration testing?',
                 ['Autoryzowane testowanie bezpieczeństwa systemu w celu wykrycia podatności', 'Atak hakerski', 'Skanowanie antywirusowe', 'Audyt kodu źródłowego'], 0),
                ('Co to jest SQL Injection?',
                 ['Wstrzyknięcie złośliwego kodu SQL do zapytania bazy danych', 'Typ protokołu sieciowego', 'Metoda hashowania haseł', 'Format exportu danych'], 0),
                ('Co to jest XSS (Cross-Site Scripting)?',
                 ['Wstrzyknięcie złośliwego skryptu do strony wyświetlanej innym użytkownikom', 'Atak siłowy na hasło', 'Typ szyfrowania', 'Protokół uwierzytelniania'], 0),
                ('Do czego służy Burp Suite?',
                 ['Przechwytywania i analizy ruchu HTTP/HTTPS podczas testów bezpieczeństwa', 'Skanowania portów', 'Zarządzania sieciami VPN', 'Analizy malware'], 0),
            ],
            'CI/CD z GitHub Actions i GitLab': [
                ('Co oznacza CI w CI/CD?',
                 ['Continuous Integration — automatyczne scalanie i testowanie kodu', 'Code Inspection', 'Container Infrastructure', 'Cloud Integration'], 0),
                ('Do czego służy pipeline CI/CD?',
                 ['Automatyzacji budowania, testowania i wdrażania aplikacji', 'Zarządzania repozytoriami', 'Monitorowania wydajności', 'Dokumentowania API'], 0),
                ('Czym jest artefakt budowania?',
                 ['Wynikiem etapu build (np. plik JAR, obraz Docker, bundle JS)', 'Zmienną środowiskową', 'Skryptem testowym', 'Gałęzią Git'], 0),
                ('Co to semantic versioning (SemVer)?',
                 ['System wersjonowania MAJOR.MINOR.PATCH z jasno określonymi zasadami', 'Algorytm kompresji kodu', 'Strategią branching', 'Typem tagów Git'], 0),
            ],
            'Linux — Administracja i Skrypty Bash': [
                ('Co robi polecenie chmod 755 plik?',
                 ['Nadaje właścicielowi pełne prawa, grupie i innym prawa odczytu i wykonania', 'Usuwa plik', 'Kopiuje plik', 'Kompresuje plik'], 0),
                ('Czym jest cron?',
                 ['Harmonogramem zadań wykonywanych cyklicznie w systemie Linux', 'Edytorem tekstu', 'Systemem plików', 'Protokołem SSH'], 0),
                ('Co robi polecenie grep -r "tekst" .?',
                 ['Rekurencyjnie przeszukuje wszystkie pliki w bieżącym katalogu', 'Usuwa pliki zawierające tekst', 'Kompresuje znalezione pliki', 'Wyświetla procesy'], 0),
                ('Czym jest potok (pipe) | w bash?',
                 ['Przekierowuje wyjście jednego polecenia na wejście drugiego', 'Operatorem logicznym OR', 'Zmienną globalną', 'Komentarzem w skrypcie'], 0),
            ],
            'Python dla Analityków Danych': [
                ('Do czego służy biblioteka Pandas?',
                 ['Analizy i manipulacji danymi tabelarycznymi (DataFrame)', 'Wizualizacji 3D', 'Głębokiego uczenia', 'Przetwarzania obrazów'], 0),
                ('Co zwraca df.describe() w Pandas?',
                 ['Podstawowe statystyki opisowe (count, mean, std, min, max, kwartyle)', 'Schemat kolumn', 'Wykres rozkładu', 'Pierwsze 5 wierszy'], 0),
                ('Co robi funkcja groupby()?',
                 ['Grupuje wiersze według wartości kolumny i umożliwia agregacje', 'Sortuje DataFrame', 'Łączy dwa DataFrame', 'Usuwa duplikaty'], 0),
                ('Jak wczytać plik CSV do Pandas?',
                 ['pd.read_csv("plik.csv")', 'pd.load("plik.csv")', 'pd.open("plik.csv")', 'pd.import_csv("plik.csv")'], 0),
            ],
            'Machine Learning z scikit-learn': [
                ('Czym jest overfitting?',
                 ['Model nadmiernie dopasowany do danych treningowych, słabo generalizuje', 'Model zbyt prosty', 'Brak danych treningowych', 'Błąd importu biblioteki'], 0),
                ('Co to cross-validation?',
                 ['Technika oceny modelu przez wielokrotny podział danych na train/test', 'Algorytm klasyfikacji', 'Metoda normalizacji', 'Typ sieci neuronowej'], 0),
                ('Do czego służy macierz pomyłek (confusion matrix)?',
                 ['Oceny jakości klasyfikatora: TP, TN, FP, FN', 'Wizualizacji danych', 'Doboru hiperparametrów', 'Normalizacji danych'], 0),
                ('Czym różni się klasyfikacja od regresji?',
                 ['Klasyfikacja przewiduje klasy dyskretne, regresja wartości ciągłe', 'Regresja jest szybsza', 'Klasyfikacja wymaga więcej danych', 'Brak różnic'], 0),
            ],
            'Flutter — Wieloplatformowe Aplikacje': [
                ('Co to Widget w Flutter?',
                 ['Podstawowy element budulcowy interfejsu użytkownika', 'Klasa abstrakcyjna Dart', 'Protokół sieciowy', 'System nawigacji'], 0),
                ('Czym różni się StatelessWidget od StatefulWidget?',
                 ['StatefulWidget może zmieniać stan i przebudowywać UI, StatelessWidget nie', 'StatelessWidget jest szybszy do renderowania', 'Brak różnic', 'StatefulWidget jest przestarzały'], 0),
                ('Jakim językiem piszemy aplikacje Flutter?',
                 ['Dart', 'Kotlin', 'Swift', 'JavaScript'], 0),
                ('Do czego służy setState()?',
                 ['Aktualizacji stanu widżetu i wyzwolenia przebudowania UI', 'Nawigacji między ekranami', 'Pobierania danych z API', 'Zarządzania zależnościami'], 0),
            ],
            'Android z Kotlin — Kurs Kompletny': [
                ('Jaki język jest oficjalnie preferowany do Android development?',
                 ['Kotlin', 'Java', 'Swift', 'Dart'], 0),
                ('Co to jest Activity w Android?',
                 ['Ekran aplikacji z interfejsem użytkownika', 'Usługa tła', 'Provider danych', 'Menedżer zasobów'], 0),
                ('Do czego służy ViewModel w architekturze MVVM?',
                 ['Przechowuje i zarządza danymi UI niezależnie od cyklu życia Activity', 'Renderuje widok', 'Zarządza bazą danych', 'Obsługuje sieć'], 0),
                ('Co to jest Jetpack Compose?',
                 ['Nowoczesny deklaratywny toolkit UI dla Androida', 'Biblioteka HTTP', 'System nawigacji', 'Narzędzie do testów'], 0),
            ],
        }

        # Tworzenie kursów, materiałów i quizów
        course_objects = {}   # title -> (course, [materials])
        for (creator, title, desc, cat, lvl, tags, dur, status, text_content) in COURSES:
            days = 70 if status == 'ACTIVE' else (30 if status == 'REVIEW' else 10)
            c = make_course(creator, title, desc, cat, lvl, tags, dur, status, days_ago=days)

            m1 = make_material(c, 'Wprowadzenie i teoria', 'VIDEO', '', 1, 2400)
            m2 = make_material(c, 'Materiały i notatki', 'TEXT', text_content, 2, 0)
            m3 = make_material(c, 'Ćwiczenia praktyczne', 'VIDEO', '', 3, 3600)
            m4 = make_material(c, 'Sprawdzian wiedzy', 'QUIZ', '', 4, 0)

            quiz = make_quiz(c, m4, f'Quiz — {title}', QUIZ_DATA.get(title, [
                ('Przykładowe pytanie?', ['Odpowiedź A', 'Odpowiedź B', 'Odpowiedź C', 'Odpowiedź D'], 0),
            ]))

            course_objects[title] = (c, [m1, m2, m3, m4])

        w(ok(f'  [OK] Utworzono {len(COURSES)} kursow z materialami i quizami.'))

        # ══════════════════════════════════════════════════════════════════════
        # 4. ZAPISY STUDENTÓW I POSTĘP
        # ══════════════════════════════════════════════════════════════════════
        w(hi('>>> Tworzenie zapisow i postepu studentow...'))

        def get_c(title):
            return course_objects.get(title)

        # (student, title, completed_count [0-4], enrolled_days_ago)
        ENROLLMENTS = [
            # Jan Malinowski — aktywny student frontend
            (s1, 'Vue.js 3 — Kompletny Przewodnik',           4, 55),
            (s1, 'CSS Grid i Flexbox — Mistrzostwo Layoutu',  2, 50),
            (s1, 'Docker i Kubernetes — Konteneryzacja Aplikacji', 1, 40),
            (s1, 'Python dla Analityków Danych',               0, 20),

            # Monika Zając — design i frontend
            (s2, 'Vue.js 3 — Kompletny Przewodnik',           3, 52),
            (s2, 'Projektowanie UX/UI dla Programistów',       4, 48),
            (s2, 'TypeScript od Podstaw do Zaawansowanego',    2, 35),
            (s2, 'CSS Grid i Flexbox — Mistrzostwo Layoutu',   1, 22),

            # Tomasz Kowalski — backend
            (s3, 'Django REST Framework — API od A do Z',      4, 50),
            (s3, 'PostgreSQL — Optymalizacja Zapytań',         3, 45),
            (s3, 'Node.js i Express — Nowoczesne API',         1, 30),
            (s3, 'MongoDB — Bazy NoSQL w Praktyce',            0, 15),

            # Karolina Lis — data science
            (s4, 'Python dla Analityków Danych',               4, 48),
            (s4, 'Machine Learning z scikit-learn',            2, 35),
            (s4, 'Flutter — Wieloplatformowe Aplikacje',       1, 20),

            # Adam Wierzbicki — security & devops
            (s5, 'Ethical Hacking — Podstawy Cyberbezpieczeństwa', 3, 45),
            (s5, 'Linux — Administracja i Skrypty Bash',       4, 40),
            (s5, 'CI/CD z GitHub Actions i GitLab',            2, 30),
            (s5, 'Docker i Kubernetes — Konteneryzacja Aplikacji', 1, 18),

            # Natalia Dąbrowska — design + Vue
            (s6, 'Vue.js 3 — Kompletny Przewodnik',           2, 38),
            (s6, 'CSS Grid i Flexbox — Mistrzostwo Layoutu',   4, 35),
            (s6, 'Projektowanie UX/UI dla Programistów',       3, 25),

            # Michał Szymański — fullstack
            (s7, 'Django REST Framework — API od A do Z',      2, 35),
            (s7, 'MongoDB — Bazy NoSQL w Praktyce',            4, 32),
            (s7, 'Node.js i Express — Nowoczesne API',         2, 22),
            (s7, 'Vue.js 3 — Kompletny Przewodnik',            1, 10),

            # Aleksandra Wójcik — data science & mobile
            (s8, 'Machine Learning z scikit-learn',            4, 30),
            (s8, 'Python dla Analityków Danych',               3, 28),
            (s8, 'Flutter — Wieloplatformowe Aplikacje',       2, 18),

            # Paweł Nowak — devops
            (s9, 'Docker i Kubernetes — Konteneryzacja Aplikacji', 4, 24),
            (s9, 'CI/CD z GitHub Actions i GitLab',            3, 20),
            (s9, 'Linux — Administracja i Skrypty Bash',       2, 14),

            # Zofia Kamińska — typescript & frontend
            (s10, 'TypeScript od Podstaw do Zaawansowanego',   4, 20),
            (s10, 'Vue.js 3 — Kompletny Przewodnik',           2, 15),
            (s10, 'CSS Grid i Flexbox — Mistrzostwo Layoutu',  1, 8),
        ]

        for (student, title, completed, enr_days) in ENROLLMENTS:
            co = get_c(title)
            if not co:
                continue
            course, mats = co
            cid = str(course.id)
            uid_s = str(student.id)

            enrolled_at = ago(enr_days)
            completed_at = ago(enr_days - 15) if completed == 4 else None

            e = Enrollment(
                user_id=uid_s,
                course_id=cid,
                enrolled_at=enrolled_at,
                completed_at=completed_at,
            )
            e.save()

            if completed > 0:
                done_ids = [str(m.id) for m in mats[:completed]]
                video_text_done = sum(
                    1 for m in mats[:completed] if m.type in ('VIDEO', 'TEXT')
                )
                xp = video_text_done * 10
                p = Progress(
                    user_id=uid_s,
                    course_id=cid,
                    completed_material_ids=done_ids,
                    xp_earned=xp,
                    last_activity_at=ago(enr_days - completed * 3),
                )
                p.save()

        w(ok(f'  [OK] Utworzono {len(ENROLLMENTS)} zapisow z postepem.'))

        # ══════════════════════════════════════════════════════════════════════
        # 5. OSIĄGNIĘCIA
        # ══════════════════════════════════════════════════════════════════════
        w(hi('>>> Przyznawanie odznak...'))

        def grant(user, badge_id, days_ago_val=20):
            info = BADGE_CATALOGUE.get(badge_id, {})
            Achievement(
                user_id=str(user.id),
                badge_id=badge_id,
                xp_value=info.get('xp', 0),
                earned_at=ago(days_ago_val),
            ).save()

        # Wszyscy studenci mają first_enrollment
        for student in [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]:
            grant(student, 'first_enrollment', 50)

        # Studenci, którzy ukończyli kurs (completed == 4)
        for student in [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]:
            grant(student, 'first_completion', 30)

        # XP >= 100 (3+ VIDEO/TEXT ukończone = 30 XP, więc 10+ materiałów = 100)
        # Szacunek: większość studentów ma >10 VIDEO/TEXT = >100 XP
        for student in [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]:
            grant(student, 'xp_100', 20)

        # XP >= 500 — tylko bardzo aktywni
        for student in [s1, s3, s5]:
            grant(student, 'xp_500', 10)

        w(ok('  [OK] Odznaki przyznane.'))

        # ══════════════════════════════════════════════════════════════════════
        # 6. POWIADOMIENIA
        # ══════════════════════════════════════════════════════════════════════
        w(hi('>>> Tworzenie powiadomien...'))

        def notif(user, ntype, title, body, read=False, days=5):
            Notification(
                user_id=str(user.id),
                type=ntype,
                title=title,
                body=body,
                is_read=read,
                created_at=ago(days),
            ).save()

        notif(s1, 'ACHIEVEMENT', 'Odznaka: Pierwsza lekcja!', 'Ukończyłeś swój pierwszy kurs — tak trzymaj!', read=True, days=30)
        notif(s1, 'ACHIEVEMENT', 'Odznaka: 500 XP!', 'Zebrałeś 500 punktów doświadczenia. Jesteś w top 10% studentów!', read=False, days=10)
        notif(s1, 'COURSE', 'Nowe materiały w Vue.js 3', 'Dodano nowe ćwiczenia do kursu Vue.js 3.', read=False, days=3)

        notif(s2, 'ACHIEVEMENT', 'Odznaka: Pierwszy zapis!', 'Witamy na platformie DJIC!', read=True, days=52)
        notif(s2, 'COURSE', 'Kurs UX/UI ukończony!', 'Gratulacje! Ukończyłaś kurs Projektowanie UX/UI.', read=False, days=15)
        notif(s2, 'PROGRESS', 'Postęp: 75% kursu Vue.js', 'Jesteś już w 75% kursu Vue.js 3. Jeszcze trochę!', read=False, days=5)

        notif(s3, 'ACHIEVEMENT', 'Odznaka: Django Master!', 'Ukończyłeś kurs Django REST Framework na poziomie ADVANCED.', read=True, days=20)
        notif(s3, 'INFO', 'Nowy kurs: Node.js i Express', 'Sprawdź nowy kurs w kategorii Backend.', read=False, days=8)

        notif(s4, 'ACHIEVEMENT', 'Odznaka: Data Scientist!', 'Ukończyłaś kurs Python dla Analityków Danych.', read=True, days=18)
        notif(s4, 'PROGRESS', 'Postęp w ML', 'Masz 50% kursu Machine Learning za sobą!', read=False, days=4)

        notif(s5, 'ACHIEVEMENT', 'Odznaka: 500 XP!', 'Osiągnąłeś 500 XP — dołączyłeś do elity platformy!', read=False, days=10)
        notif(s5, 'COURSE', 'Linux — Kurs ukończony', 'Ukończyłeś kurs Linux — Administracja i Skrypty Bash.', read=True, days=22)

        notif(s6, 'ACHIEVEMENT', 'Odznaka: CSS Wizard!', 'Ukończyłaś kurs CSS Grid i Flexbox.', read=False, days=12)
        notif(s7, 'COURSE', 'MongoDB — Kurs ukończony', 'Gratulacje! Ukończyłeś kurs MongoDB.', read=True, days=14)
        notif(s8, 'ACHIEVEMENT', 'Odznaka: ML Expert!', 'Ukończyłaś kurs Machine Learning z scikit-learn.', read=False, days=8)
        notif(s9, 'ACHIEVEMENT', 'Odznaka: DevOps Pro!', 'Ukończyłeś kurs Docker i Kubernetes.', read=True, days=10)
        notif(s10, 'ACHIEVEMENT', 'Odznaka: TypeScript Hero!', 'Ukończyłaś kurs TypeScript od Podstaw.', read=False, days=6)

        # Powiadomienia dla kreatorów (kurs zatwierdzony)
        notif(anna, 'COURSE', 'Kurs zatwierdzony: Vue.js 3', 'Twój kurs Vue.js 3 został zatwierdzony i jest teraz widoczny dla studentów.', read=True, days=65)
        notif(anna, 'INFO', 'Oczekuje recenzji: React 18', 'Kurs React 18 i Next.js oczekuje na recenzję administratora.', read=False, days=2)
        notif(marek, 'COURSE', 'Kurs zatwierdzony: Django REST', 'Twój kurs Django REST Framework został zatwierdzony!', read=True, days=60)
        notif(piotr, 'COURSE', 'Kurs zatwierdzony: Docker', 'Kurs Docker i Kubernetes jest już aktywny.', read=True, days=62)
        notif(julia, 'INFO', 'Oczekuje recenzji: Android Kotlin', 'Kurs Android z Kotlin oczekuje na zatwierdzenie przez admina.', read=False, days=3)

        w(ok('  [OK] Powiadomienia utworzone.'))

        # ======================================================================
        # PODSUMOWANIE
        # ======================================================================
        w('')
        w(ok('=========================================='))
        w(ok('  DANE DEMO ZALADOWANE POMYSLNIE!'))
        w(ok('=========================================='))
        w(f'  Uzytkownicy : 1 admin + 4 kreatorow + 10 studentow')
        w(f'  Kursy        : 15 ACTIVE, 1 REVIEW, 1 DRAFT')
        w(f'  Materialy    : {len(COURSES) * 4} (po 4 na kurs)')
        w(f'  Quizy        : {len(COURSES)} (po 1 na kurs)')
        w(f'  Zapisy       : {len(ENROLLMENTS)}')
        w(f'  Powiadomienia: {Notification.objects.count()}')
        w(ok('=========================================='))
