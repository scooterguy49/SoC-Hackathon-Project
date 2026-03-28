from main import app

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")