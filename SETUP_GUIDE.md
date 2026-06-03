# ESG Platform V2 — Complete Setup Guide
# Vue.js + Node.js + Python Azure Functions (all local, no Azure account needed)

═══════════════════════════════════════════════════════════════════════
WHAT YOU'RE BUILDING
═══════════════════════════════════════════════════════════════════════

  Browser (Vue.js :5173)
       ↓ /api/*
  Node.js Express (:3001)          ← API gateway / proxy
       ↓ HTTP
  Azure Functions Python (:7071)   ← All KPI logic (your app.py)
       ↓
  Local JSON files / CSV           ← Data store (no DB needed yet)

You run THREE terminals. Everything runs on localhost. No cloud needed.


═══════════════════════════════════════════════════════════════════════
STEP 0 — CHECK PREREQUISITES (install what's missing)
═══════════════════════════════════════════════════════════════════════

Check Node.js (need v18+):
  node --version

  If missing → https://nodejs.org  → download LTS → install → restart terminal

Check Python (need 3.10+):
  python --version   (or python3 --version on Mac/Linux)

  If missing → https://python.org/downloads → install

Check Azure Functions Core Tools (need v4):
  func --version

  If missing, install:

  Windows (run in PowerShell as Admin):
    npm install -g azure-functions-core-tools@4 --unsafe-perm true

  Mac:
    brew tap azure/functions
    brew install azure-functions-core-tools@4

  Linux (Debian/Ubuntu):
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
    sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
    sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/debian/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
    sudo apt-get update
    sudo apt-get install azure-functions-core-tools-4

  Verify:
    func --version   → should show 4.x.x


═══════════════════════════════════════════════════════════════════════
STEP 1 — CREATE THE FOLDER STRUCTURE
═══════════════════════════════════════════════════════════════════════

Open a terminal and run these commands exactly:

  mkdir esg-v2
  cd esg-v2

  mkdir -p frontend/src/views
  mkdir -p frontend/src/components
  mkdir -p frontend/src/stores
  mkdir -p frontend/src/services
  mkdir -p frontend/src/assets
  mkdir -p frontend/public
  mkdir -p backend/routes
  mkdir -p backend/controllers
  mkdir -p backend/services
  mkdir -p python-service/shared
  mkdir -p python-service/calculate_kpi
  mkdir -p python-service/get_companies
  mkdir -p python-service/get_analytics
  mkdir -p python-service/get_benchmarks
  mkdir -p python-service/submit_data
  mkdir -p python-service/data

After running, your structure should look like:

  esg-v2/
  ├── frontend/
  │   ├── public/
  │   └── src/
  │       ├── assets/
  │       ├── components/
  │       ├── services/
  │       ├── stores/
  │       └── views/
  ├── backend/
  │   ├── routes/
  │   ├── controllers/
  │   └── services/
  └── python-service/
      ├── data/              ← submissions stored here as JSON
      ├── shared/
      ├── calculate_kpi/
      ├── get_companies/
      ├── get_analytics/
      ├── get_benchmarks/
      └── submit_data/


═══════════════════════════════════════════════════════════════════════
STEP 2 — PASTE ALL FILES
═══════════════════════════════════════════════════════════════════════

From the downloaded zip (or copy from the generated files), paste each
file into the correct folder. The complete file list is:

  PYTHON SERVICE (python-service/):
  ├── host.json
  ├── local.settings.json
  ├── requirements.txt
  ├── shared/__init__.py
  ├── shared/calculations.py
  ├── shared/verification.py
  ├── shared/data_loader.py
  ├── calculate_kpi/__init__.py
  ├── calculate_kpi/function.json
  ├── get_companies/__init__.py
  ├── get_companies/function.json
  ├── get_analytics/__init__.py
  ├── get_analytics/function.json
  ├── get_benchmarks/__init__.py
  ├── get_benchmarks/function.json
  ├── submit_data/__init__.py
  └── submit_data/function.json

  NODE BACKEND (backend/):
  ├── package.json
  ├── .env
  ├── server.js
  ├── routes/companies.js
  ├── routes/analytics.js
  ├── routes/benchmarks.js
  ├── routes/submissions.js
  └── services/pythonService.js

  FRONTEND (frontend/):
  ├── index.html
  ├── package.json
  ├── vite.config.js
  ├── tailwind.config.js
  ├── postcss.config.js
  └── src/
      ├── main.js
      ├── App.vue
      ├── assets/main.css
      ├── router/index.js
      ├── stores/auth.js
      ├── services/api.js
      ├── components/Sidebar.vue
      ├── components/Navbar.vue
      ├── components/KPICard.vue
      └── views/
          ├── Login.vue
          ├── Dashboard.vue
          ├── Entry.vue
          ├── Analysis.vue
          ├── Benchmarking.vue
          ├── Reports.vue
          └── Admin.vue


═══════════════════════════════════════════════════════════════════════
STEP 3 — SET UP PYTHON SERVICE
═══════════════════════════════════════════════════════════════════════

Open Terminal 1. Navigate to the python-service folder:

  cd esg-v2/python-service

Create a Python virtual environment:

  Windows:
    python -m venv .venv
    .venv\Scripts\activate

  Mac/Linux:
    python3 -m venv .venv
    source .venv/bin/activate

You should see (.venv) at the start of your terminal prompt.

Install dependencies:

  pip install -r requirements.txt

Verify it worked:

  pip list   → you should see azure-functions in the list

Start the Python Functions:

  func start

Expected output:
  Azure Functions Core Tools
  Functions:
    calculate_kpi: [POST] http://localhost:7071/api/calculate_kpi
    get_analytics: [GET]  http://localhost:7071/api/get_analytics
    get_benchmarks:[GET]  http://localhost:7071/api/get_benchmarks
    get_companies: [GET]  http://localhost:7071/api/get_companies
    submit_data:   [POST] http://localhost:7071/api/submit_data

KEEP THIS TERMINAL OPEN. Do not close it.


═══════════════════════════════════════════════════════════════════════
STEP 4 — SET UP NODE.JS BACKEND
═══════════════════════════════════════════════════════════════════════

Open Terminal 2 (new terminal window). Navigate to backend:

  cd esg-v2/backend

Install dependencies:

  npm install

Start the Node server:

  npm run dev   (uses nodemon — auto-restarts on file changes)
  or
  npm start     (regular node)

Expected output:
  ESG Backend running at http://localhost:3001
  Proxying Python Functions at http://localhost:7071/api

Test it works (open in browser or run in a third terminal):

  curl http://localhost:3001/api/health
  → {"status":"ok","service":"esg-backend"}

KEEP THIS TERMINAL OPEN.


═══════════════════════════════════════════════════════════════════════
STEP 5 — SET UP VUE.JS FRONTEND
═══════════════════════════════════════════════════════════════════════

Open Terminal 3 (new terminal window). Navigate to frontend:

  cd esg-v2/frontend

Install dependencies:

  npm install

This installs Vue 3, Vite, Tailwind CSS, Chart.js, Pinia, Vue Router.
It may take 1-2 minutes. You'll see a node_modules folder appear.

Start the Vue dev server:

  npm run dev

Expected output:
  VITE v5.x.x  ready in 400ms
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose

Open http://localhost:5173 in your browser.

KEEP THIS TERMINAL OPEN.


═══════════════════════════════════════════════════════════════════════
STEP 6 — FIRST RUN & LOGIN
═══════════════════════════════════════════════════════════════════════

Open your browser at:  http://localhost:5173

You'll see the dss+360 login page.

Demo credentials:

  TIP CLIENT role:
    Email:    verdatyres@tip.com
    Password: tip2024

  DSS+ ANALYST role:
    Email:    analyst@consultdss.com
    Password: dss2024

After logging in you'll see the full dashboard.

The role switcher on the login page changes which navigation
pages are shown (client vs dss+ analyst views).


═══════════════════════════════════════════════════════════════════════
STEP 7 — VERIFY THE PYTHON API IS CONNECTED
═══════════════════════════════════════════════════════════════════════

Go to the Submit Data page and fill in a field.
Watch Terminal 1 (Python Functions) — you should see:

  Executing 'calculate_kpi' ...
  Executed 'calculate_kpi' (Succeeded, ...)

If you see this, the full stack is working:
  Vue → Node → Python Functions → response → Vue

If you don't see it (or get an error), the KPI sidebar will
stay at demo values — this is expected fallback behaviour
and doesn't break anything.


═══════════════════════════════════════════════════════════════════════
DAILY WORKFLOW — HOW TO START THE APP EACH DAY
═══════════════════════════════════════════════════════════════════════

Open 3 terminals and run one command in each:

  Terminal 1 (Python):
    cd esg-v2/python-service
    source .venv/bin/activate   (Mac/Linux)
    .venv\Scripts\activate      (Windows)
    func start

  Terminal 2 (Node):
    cd esg-v2/backend
    npm run dev

  Terminal 3 (Vue):
    cd esg-v2/frontend
    npm run dev

Then open: http://localhost:5173


═══════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════

PROBLEM: "func: command not found"
FIX:     Install Azure Functions Core Tools (see Step 0)
         On Windows, restart your terminal after npm install -g

PROBLEM: "Port 7071 already in use"
FIX:     Another process is using port 7071.
         Windows: netstat -ano | findstr :7071  → taskkill /PID <id> /F
         Mac:     lsof -ti:7071 | xargs kill -9

PROBLEM: "Port 3001 already in use"
FIX:     Change PORT in backend/.env to 3002
         Update vite.config.js proxy target to http://localhost:3002

PROBLEM: "Cannot find module 'azure-functions'"
FIX:     You forgot to activate the virtual environment.
         Run: source .venv/bin/activate (Mac) or .venv\Scripts\activate (Windows)
         Then: pip install -r requirements.txt

PROBLEM: Vue shows error "Network Error" when submitting data
FIX:     The Python Functions or Node backend isn't running.
         Check Terminal 1 and Terminal 2 are both showing running.

PROBLEM: "ModuleNotFoundError: No module named 'shared'"
FIX:     The sys.path.insert in each __init__.py should fix this.
         If not, run func start from inside the python-service directory,
         not from esg-v2 root.

PROBLEM: Tailwind styles not working (unstyled page)
FIX:     Make sure postcss.config.js exists in the frontend folder.
         Stop and restart: npm run dev


═══════════════════════════════════════════════════════════════════════
PROJECT STRUCTURE — FINAL OVERVIEW
═══════════════════════════════════════════════════════════════════════

esg-v2/
├── .gitignore
│
├── frontend/                        Vue.js app (port 5173)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js               proxy /api → localhost:3001
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── main.js                  app entry point
│       ├── App.vue                  root layout (sidebar + navbar)
│       ├── assets/main.css          Tailwind base
│       ├── router/index.js          Vue Router (Login, Dashboard, etc.)
│       ├── stores/auth.js           Pinia auth store (local demo auth)
│       ├── services/api.js          all axios API calls
│       ├── components/
│       │   ├── Sidebar.vue          nav sidebar (role-aware)
│       │   ├── Navbar.vue           top bar
│       │   └── KPICard.vue          reusable KPI card
│       └── views/
│           ├── Login.vue            login page
│           ├── Dashboard.vue        KPI overview + charts
│           ├── Entry.vue            6-step data entry wizard
│           ├── Analysis.vue         all KPI charts (4 sections)
│           ├── Benchmarking.vue     quartile bands + scorecard
│           ├── Reports.vue          CSR summary + PDF download
│           └── Admin.vue            dss+ verification queue
│
├── backend/                         Node.js API gateway (port 3001)
│   ├── package.json
│   ├── .env                         PORT + PYTHON_SERVICE_URL
│   ├── server.js                    Express app
│   ├── routes/
│   │   ├── companies.js
│   │   ├── analytics.js
│   │   ├── benchmarks.js
│   │   └── submissions.js
│   └── services/
│       └── pythonService.js         calls Python Functions
│
└── python-service/                  Azure Functions (port 7071)
    ├── host.json
    ├── local.settings.json          local env config (never commit)
    ├── requirements.txt
    ├── data/                        local JSON data store
    │   └── submissions.json         auto-created on first save
    ├── shared/                      your app.py logic, extracted
    │   ├── __init__.py
    │   ├── calculations.py          all KPI formulas
    │   ├── verification.py          YoY flag rules
    │   └── data_loader.py           read/write submissions
    ├── calculate_kpi/               POST — live KPI calc (no save)
    ├── submit_data/                 POST — save full submission
    ├── get_companies/               GET  — company list + status
    ├── get_analytics/               GET  — historical KPI series
    └── get_benchmarks/              GET  — quartile bands + scorecard


═══════════════════════════════════════════════════════════════════════
WHEN YOU'RE READY FOR AZURE (FREE TIER)
═══════════════════════════════════════════════════════════════════════

Azure free tier gives you:
  - Azure Functions: 1 million free executions/month (plenty)
  - Azure Static Web Apps: free plan (hosts Vue build)
  - Azure SQL: free 32GB for 12 months (or use free JSON tier)

Steps when ready:
  1. Create Azure account at portal.azure.com
  2. Create a Function App (Python 3.11, Consumption plan = free)
  3. Deploy:  func azure functionapp publish <your-app-name>
  4. Update backend/.env:
       PYTHON_SERVICE_URL=https://your-app.azurewebsites.net/api
  5. Build Vue:  npm run build  (creates dist/ folder)
  6. Deploy frontend to Azure Static Web Apps
     (connects to your GitHub repo, auto-deploys on push)

That's it. The code doesn't change — only the URLs change.


═══════════════════════════════════════════════════════════════════════
KEEPING YOUR OLD STREAMLIT APP RUNNING
═══════════════════════════════════════════════════════════════════════

The old Streamlit project is completely separate.
This V2 project lives in a different folder (esg-v2/).
Your original repo at github.com/vedantbhatiaa/esg is untouched.

To still run the old app alongside V2:
  cd /path/to/original/esg
  streamlit run app.py            runs on localhost:8501

Both can run at the same time — they use different ports.
