from chalice import Chalice


app = Chalice(app_name="users")


@app.route("/users")
def get_users() -> list[str]:
    return ["user", "user2"]