from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4
import secrets

from flask import (
	Flask,
	flash,
	redirect,
	render_template,
	request,
	send_from_directory,
	session,
	url_for,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "menu_items.json"
CAT_FILE = BASE_DIR / "data" / "categories.json"
REPO_DIR = BASE_DIR / "repositorio"
DEFAULT_CATEGORIES = ["doses", "porções", "bebidas", "espetinhos"]


def create_app() -> Flask:
	app = Flask(__name__)
	app.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
	app.config["ADMIN_PASSWORD"] = os.getenv("ADMIN_PASSWORD", "admin123")

	ensure_data_file()
	ensure_categories_file()

	@app.route("/")
	def index() -> str:
		items = load_items()
		categories = load_categories()
		grouped = {category: [] for category in categories}
		fallback_category = categories[0] if categories else DEFAULT_CATEGORIES[0]
		for item in items:
			category = item.get("category", fallback_category)
			if category not in grouped:
				grouped[fallback_category].append(item)
				continue
			grouped[category].append(item)

		return render_template(
			"index.html",
			grouped=grouped,
			categories=categories,
			has_video=(REPO_DIR / "video.mp4").exists(),
		)

	@app.route("/admin", methods=["GET", "POST"])
	def admin_login() -> str:
		if request.method == "POST":
			password = request.form.get("password", "")
			if password == app.config["ADMIN_PASSWORD"]:
				session["is_admin"] = True
				return redirect(url_for("admin_panel"))
			flash("Senha incorreta.", "error")

		return render_template("admin_login.html")

	@app.route("/admin/logout")
	def admin_logout() -> Any:
		session.pop("is_admin", None)
		flash("Sessao de admin encerrada.", "success")
		return redirect(url_for("admin_login"))

	@app.route("/admin/painel")
	def admin_panel() -> Any:
		if not session.get("is_admin"):
			return redirect(url_for("admin_login"))

		return render_template(
			"admin.html",
			items=load_items(),
			categories=load_categories(),
			image_files=list_media_files(extensions={".jpg", ".jpeg", ".png", ".webp", ".gif"}),
		)

	@app.route("/admin/category/add", methods=["POST"])
	def add_category() -> Any:
		if not session.get("is_admin"):
			return redirect(url_for("admin_login"))

		name = normalize_category_name(request.form.get("name", ""))
		if not name:
			flash("Informe um nome de categoria valido.", "error")
			return redirect(url_for("admin_panel"))

		categories = load_categories()
		if name in categories:
			flash("Essa categoria ja existe.", "error")
			return redirect(url_for("admin_panel"))

		categories.append(name)
		save_categories(categories)
		flash("Categoria adicionada com sucesso.", "success")
		return redirect(url_for("admin_panel"))

	@app.route("/admin/item/add", methods=["POST"])
	def add_item() -> Any:
		if not session.get("is_admin"):
			return redirect(url_for("admin_login"))

		item = form_to_item(request.form)
		items = load_items()
		items.append(item)
		save_items(items)
		flash("Item adicionado com sucesso.", "success")
		return redirect(url_for("admin_panel"))

	@app.route("/admin/item/<item_id>/edit", methods=["POST"])
	def edit_item(item_id: str) -> Any:
		if not session.get("is_admin"):
			return redirect(url_for("admin_login"))

		items = load_items()
		for idx, existing in enumerate(items):
			if existing.get("id") == item_id:
				updated = form_to_item(request.form)
				updated["id"] = item_id
				items[idx] = updated
				save_items(items)
				flash("Item atualizado com sucesso.", "success")
				break
		else:
			flash("Item nao encontrado.", "error")

		return redirect(url_for("admin_panel"))

	@app.route("/admin/item/<item_id>/delete", methods=["POST"])
	def delete_item(item_id: str) -> Any:
		if not session.get("is_admin"):
			return redirect(url_for("admin_login"))

		items = load_items()
		new_items = [item for item in items if item.get("id") != item_id]
		if len(new_items) == len(items):
			flash("Item nao encontrado.", "error")
		else:
			save_items(new_items)
			flash("Item removido com sucesso.", "success")

		return redirect(url_for("admin_panel"))

	@app.route("/media/<path:filename>")
	def media_file(filename: str) -> Any:
		return send_from_directory(REPO_DIR, filename)

	return app


def ensure_data_file() -> None:
	DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
	if DATA_FILE.exists():
		return

	default_items = [
		{
			"id": str(uuid4()),
			"name": "Frango a passarinho",
			"category": "porções",
			"price": 39.90,
			"description": "Porcao crocante e temperada, ideal para compartilhar.",
			"image": "frango a passarinho.jpg",
		},
		{
			"id": str(uuid4()),
			"name": "Refrigerante lata",
			"category": "bebidas",
			"price": 7.00,
			"description": "Consulte sabores disponiveis no estabelecimento.",
			"image": "",
		},
		{
			"id": str(uuid4()),
			"name": "Mousse da casa",
			"category": "doses",
			"price": 12.50,
			"description": "Sobremesa leve e cremosa, servida gelada.",
			"image": "",
		},
	]
	save_items(default_items)


def ensure_categories_file() -> None:
	CAT_FILE.parent.mkdir(parents=True, exist_ok=True)
	if CAT_FILE.exists():
		return
	save_categories(DEFAULT_CATEGORIES)


def load_items() -> list[dict[str, Any]]:
	try:
		with DATA_FILE.open("r", encoding="utf-8") as file:
			data = json.load(file)
			if isinstance(data, list):
				return data
	except (OSError, json.JSONDecodeError):
		pass
	return []


def save_items(items: list[dict[str, Any]]) -> None:
	with DATA_FILE.open("w", encoding="utf-8") as file:
		json.dump(items, file, ensure_ascii=False, indent=2)


def load_categories() -> list[str]:
	try:
		with CAT_FILE.open("r", encoding="utf-8") as file:
			data = json.load(file)
			if isinstance(data, list):
				normalized = []
				for value in data:
					name = normalize_category_name(str(value))
					if name and name not in normalized:
						normalized.append(name)
				if normalized:
					for category in DEFAULT_CATEGORIES:
						if category not in normalized:
							normalized.append(category)
					return normalized
	except (OSError, json.JSONDecodeError):
		pass

	return DEFAULT_CATEGORIES.copy()


def save_categories(categories: list[str]) -> None:
	with CAT_FILE.open("w", encoding="utf-8") as file:
		json.dump(categories, file, ensure_ascii=False, indent=2)


def form_to_item(form_data: Any) -> dict[str, Any]:
	raw_price = form_data.get("price", "0").replace(",", ".")
	try:
		price = round(float(raw_price), 2)
	except ValueError:
		price = 0.0

	categories = load_categories()
	fallback_category = categories[0] if categories else DEFAULT_CATEGORIES[0]
	category = normalize_category_name(form_data.get("category", fallback_category))
	if category not in categories:
		category = fallback_category

	options = parse_item_options(form_data)

	try:
		image_position_x = int(form_data.get("image_position_x", "50"))
	except ValueError:
		image_position_x = 50

	try:
		image_position_y = int(form_data.get("image_position_y", "50"))
	except ValueError:
		image_position_y = 50

	try:
		image_scale = float(form_data.get("image_scale", "1").replace(",", "."))
		image_scale = round(max(0.8, min(image_scale, 2.5)), 2)
	except ValueError:
		image_scale = 1.0

	item = {
		"id": str(uuid4()),
		"name": form_data.get("name", "Novo item").strip(),
		"category": category,
		"price": price,
		"options": options,
		"description": form_data.get("description", "").strip(),
		"image": form_data.get("image", "").strip(),
		"image_position_x": image_position_x,
		"image_position_y": image_position_y,
		"image_scale": image_scale,
	}

	return item


def parse_item_options(form_data: Any) -> list[dict[str, Any]]:
	names = form_data.getlist("option_name")
	prices = form_data.getlist("option_price")
	result: list[dict[str, Any]] = []

	for idx, raw_name in enumerate(names):
		name = str(raw_name).strip()
		if not name:
			continue

		raw_price = prices[idx] if idx < len(prices) else "0"
		try:
			price = round(float(str(raw_price).replace(",", ".")), 2)
		except ValueError:
			price = 0.0

		result.append({"name": name, "price": price})

	return result


def normalize_category_name(value: str) -> str:
	return " ".join(value.strip().split())


def list_media_files(extensions: set[str]) -> list[str]:
	if not REPO_DIR.exists():
		return []

	result = []
	for file in REPO_DIR.iterdir():
		if not file.is_file():
			continue
		if file.suffix.lower() in extensions:
			result.append(file.name)
	return sorted(result)


app = create_app()


if __name__ == "__main__":
	debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
	app.run(host="0.0.0.0", port=5000, debug=debug_mode)
