#!/bin/bash
# Run the Streamlit admin app

echo "🏆 Starting Scores Server Admin Panel..."
echo ""
echo "Admin credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "The app will open in your browser at http://localhost:8501"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Streamlit
streamlit run admin_app.py --server.port 8501 --server.address localhost

