@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return "Welcome to your dashboard!"