from __future__ import print_function
# import time
import os, json, requests, zipfile, shutil, subprocess
from flask import *
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lenenlauncher'

class games_path(FlaskForm):
    path1 = StringField("LE01 path :")
    path2 = StringField("LE02 path :")
    path3 = StringField("LE03 path :")
    path4 = StringField("LE04 path :")
    submit = SubmitField("Save path")

def j_read():
    with open("games.json", "r") as f:
        data = json.load(f)
    return data

def j_write(data):
    with open("games.json", 'w') as f:
        json.dump(data, f, indent=2)

@app.route("/", methods=['GET', 'POST'])
def home():
    gamespath = games_path()
    err_mess = request.args.get("err_mess", "", type=str)
    if gamespath.validate_on_submit():
        data = j_read()
        data["LE01"]["path"] = gamespath.path1.data
        data["LE02"]["path"] = gamespath.path2.data
        data["LE03"]["path"] = gamespath.path3.data
        data["LE04"]["path"] = gamespath.path4.data
        j_write(data)
        return redirect(url_for('home'))
    elif request.method == 'GET':
        data = j_read()
        gamespath.path1.data = data["LE01"]["path"]
        gamespath.path2.data = data["LE02"]["path"]
        gamespath.path3.data = data["LE03"]["path"]
        gamespath.path4.data = data["LE04"]["path"]
    return render_template("home.html", gamespath=gamespath, err_mess=err_mess)

@app.route("/launch")
def launch():
    game = request.args.get("game", None, type=str)
    cwd = os.getcwd()

    data = j_read()
    path = data[f"{game}"]["path"]
    try:
        if path == "":
            return redirect(url_for("home", err_mess=f"{game}'s path does not exists. Please set it to continue."))
        else:
            os.chdir(path)
            Le = f"L{game[1].lower()}{game[2:]}.exe"
            try: os.system(f"start {Le}")
            except:
                try: os.system(f"start {game.lower()}.exe")
                except: return redirect(url_for("home", err_mess="The executable file is not recognized (Le01.exe or le01.exe)"))
    except: return redirect(url_for("home", err_mess=f"{game}'s path is not correct. Please set it to continue."))
    os.chdir(cwd)
    return redirect(url_for("home"))

@app.route("/mods")
def mods():
    with open("games.json", 'r') as f:
        data = json.load(f)
    return render_template("mods.html", data=data)

@app.route("/download")
def download():
    wtdl = request.args.get("wtdl", None, type=str)
    if wtdl == "En_LE01":
        dl_link = "https://cdn.discordapp.com/attachments/270893446883966978/827196753807802398/Lenen_01_English_Patch_ver04b.zip"
        r = requests.get(dl_link, stream=True)
        with open("data/LE01_EN.zip", "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        with zipfile.ZipFile("data/LE01_EN.zip", 'r') as zip_ref:
            zip_ref.extractall("data/LE01_EN/")
        os.remove("data/LE01_EN.zip")
        data = j_read()
        data["LE01"]["English Patch"] = "data/LE01_EN"
        j_write(data)
        return redirect(url_for('mods'))

@app.route("/activate")
def activate():
    wta = request.args.get("wta", None, type=str)
    if wta == "En_LE01":
        data = j_read()
        cwd = os.getcwd()
        os.chdir(f'{data["LE01"]["English Patch"]}')
        os.system(f'call "Connecting Chain Handserif.ttf"')
        os.chdir(cwd)
        shutil.copytree(f'{data["LE01"]["path"]}/text_dat', "data/LE01_old/text_dat")
        shutil.copytree(f'{data["LE01"]["path"]}/text_img', "data/LE01_old/text_img")
        shutil.copy(f'{data["LE01"]["path"]}/dat.led', "data/LE01_old/dat.led")
        shutil.rmtree(f'{data["LE01"]["path"]}/text_dat')
        shutil.rmtree(f'{data["LE01"]["path"]}/text_img')
        os.remove(f'{data["LE01"]["path"]}/dat.led')
        shutil.copytree(f'{data["LE01"]["English Patch"]}/text_dat', f'{data["LE01"]["path"]}/text_dat')
        shutil.copytree(f'{data["LE01"]["English Patch"]}/text_img', f'{data["LE01"]["path"]}/text_img')
        shutil.copy(f"data/LE01_old/dat.led", f'{data["LE01"]["English Patch"]}/dat.led patch/dat.led')
        cwd = os.getcwd()
        os.chdir(f'{data["LE01"]["English Patch"]}/dat.led patch/')
        subprocess.call('start patcher.bat', shell=True)
        os.chdir(cwd)
        shutil.copy(f'{data["LE01"]["English Patch"]}/dat.led patch/dat.led', f'{data["LE01"]["path"]}/dat.led')
        data["LE01"]["En_activated"] = True
        j_write(data)
    return redirect(url_for('mods'))

@app.route("/unload")
def unload():
    pass


if __name__ == "__main__":
    app.run(host = "127.0.0.1", port = 5000)