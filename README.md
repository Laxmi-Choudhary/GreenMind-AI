🌱 GreenMind AI

GreenMind AI is an AI-powered sustainability platform designed to help individuals track, analyze, and reduce their environmental impact. The platform provides carbon footprint calculations, personalized sustainability recommendations, eco-challenges, and AI-driven insights to encourage greener lifestyles.

---

🚀 Features

🌍 Carbon Footprint Calculator

Calculate daily carbon emissions based on transportation, electricity usage, lifestyle habits, and consumption patterns.

🤖 AI Sustainability Coach

Receive personalized sustainability advice and eco-friendly recommendations powered by AI.

💬 Eco Chatbot

Interact with an intelligent chatbot to ask sustainability-related questions and receive instant responses.

🏆 Sustainability Challenges

Participate in eco-friendly challenges, earn points, and unlock badges.

📊 Reports Dashboard

Visualize your sustainability journey with reports and analytics.

🥇 Leaderboard

Compete with other users and track rankings based on sustainability performance.

🎯 SDG Dashboard

Monitor contributions toward the United Nations Sustainable Development Goals (SDGs).

🧾 Bill Analyzer

Upload utility bills and receive insights into energy consumption and savings opportunities.

🧾 Receipt Analyzer

Analyze shopping receipts to understand purchasing habits and environmental impact.

🔐 Secure Authentication

JWT-based authentication with access and refresh token support.

---

🛠 Tech Stack

Frontend

- React
- Vite
- Tailwind CSS
- React Router
- Recharts
- Lucide React

Backend

- FastAPI
- MongoDB
- SQLite (fallback database)
- Redis
- JWT Authentication
- Pydantic
- Motor (MongoDB Driver)

DevOps & Deployment

- GitHub Actions
- Render
- Vercel
- MongoDB Atlas

---

📂 Project Structure

GreenMind-AI/
│
├── backend/
│   ├── app/
│   ├── routes/
│   ├── middleware/
│   ├── utils/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── README.md
└── .gitignore

---

⚙️ Installation

Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (optional)
- Redis (optional)

---

Backend Setup

git clone https://github.com/Laxmi-Choudhary/GreenMind-AI.git

cd GreenMind-AI/backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

Create a ".env" file:

SECRET_KEY=your_secret_key
MONGODB_URI=your_mongodb_uri
DATABASE_NAME=greenmind
REDIS_URL=your_redis_url
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

Start backend:

uvicorn app.main:app --reload

Backend runs on:

http://localhost:8000

---

Frontend Setup

cd ../frontend

npm install

Create ".env":

VITE_API_URL=http://localhost:8000

Run frontend:

npm run dev

Frontend runs on:

http://localhost:5173

---

🔑 Environment Variables

Variable| Description
SECRET_KEY| JWT Secret Key
MONGODB_URI| MongoDB Connection URI
DATABASE_NAME| MongoDB Database Name
REDIS_URL| Redis Connection URL
GEMINI_API_KEY| Gemini API Key
OPENAI_API_KEY| OpenAI API Key
VITE_API_URL| Backend API URL

---

📚 API Endpoints

Authentication

- "POST /api/auth/register"
- "POST /api/auth/login"
- "POST /api/auth/logout"
- "POST /api/auth/token/refresh"
- "GET /api/auth/me"

Carbon Calculator

- "POST /api/calculator/log"
- "GET /api/calculator/history"

Chat

- "POST /api/chat"

Reports

- "GET /api/reports"

Challenges

- "GET /api/challenges"

---

🧪 Testing

Run backend tests:

cd backend
pytest -v

Run frontend build:

cd frontend
npm run build

---

🔄 CI/CD

GitHub Actions automatically:

- Builds frontend
- Runs backend tests
- Performs dependency security scans
- Checks code quality

---

📸 Screenshots

Add screenshots here:

screenshots/
├── dashboard.png
├── calculator.png
├── chatbot.png
├── leaderboard.png

Example:

![Dashboard](screenshots/dashboard.png)

---

🌐 Deployment Links

Frontend:

https://your-vercel-app.vercel.app

Backend:

https://your-render-app.onrender.com

---

🔮 Future Improvements

- Mobile application
- Social sharing features
- AI-generated sustainability reports
- Community forums
- Gamification enhancements
- Multi-language support
- Real-time notifications

---

🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

📄 License

This project is licensed under the MIT License.

---

👨‍💻 Author

Laxmi Choudhary

GitHub: https://github.com/Laxmi-Choudhary