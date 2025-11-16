#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chasse au Trésor - Version Française
- Interface entièrement en français
- Affiche les nombres en chiffres ET en lettres françaises (ex : 10 (dix))
- Modes : Classique, Chrono, Difficile
- Skins (thèmes)
- Sauvegarde des meilleurs scores dans scores.json
- Sons optionnels via pygame (silencieux si non installé)
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os
import time

# Tentative d'utiliser pygame pour sons (facultatif)
try:
    import pygame
    pygame.mixer.init()
    SON_DISPONIBLE = True
except Exception:
    SON_DISPONIBLE = False

FICHIER_SCORES = "scores.json"


# -------------------------
# Convertisseur de nombres en français (0..9999)
# -------------------------
def nombre_en_lettres(n: int) -> str:
    """
    Convertit un entier 0..9999 en représentation littérale française simple.
    Gère les règles standards pour 0..9999 (approximation correcte pour nos usages).
    """
    if n < 0:
        return "moins " + nombre_en_lettres(-n)
    if n == 0:
        return "zéro"

    unités = [
        "", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"
    ]
    spéciaux = {
        10: "dix", 11: "onze", 12: "douze", 13: "treize", 14: "quatorze",
        15: "quinze", 16: "seize"
    }
    dizaines = [
        "", "", "vingt", "trente", "quarante", "cinquante", "soixante"
    ]

    def deux_chiffres(x):
        if x < 10:
            return unités[x]
        if 10 <= x <= 16:
            return spéciaux[x]
        if 17 <= x <= 19:
            return "dix-" + unités[x - 10]
        if 20 <= x <= 69:
            d = x // 10
            u = x % 10
            base = dizaines[d]
            if u == 1:
                return base + "-et-un"
            elif u > 0:
                return base + "-" + unités[u]
            else:
                return base
        if 70 <= x <= 79:
            # 70 = soixante-dix, 71 = soixante-et-onze, ...
            rest = x - 60
            return "soixante-" + deux_chiffres(rest)
        if 80 <= x <= 99:
            # 80 = quatre-vingts (sans 's' si suite), 81 = quatre-vingt-un
            rest = x - 80
            if rest == 0:
                return "quatre-vingts"
            else:
                return "quatre-vingt-" + deux_chiffres(rest)
        return ""

    def trois_chiffres(x):
        if x < 100:
            return deux_chiffres(x)
        h = x // 100
        rest = x % 100
        if h == 1:
            prefix = "cent"
        else:
            prefix = unités[h] + " cent"
        if rest == 0:
            # cent(s) prend un 's' quand il est multiple exact et >1
            if h > 1:
                return prefix + "s"
            return prefix
        return prefix + " " + deux_chiffres(rest)

    if n < 1000:
        return trois_chiffres(n)

    milliers = n // 1000
    reste = n % 1000
    if milliers == 1:
        prefix = "mille"
    else:
        prefix = nombre_en_lettres(milliers) + " mille"
    if reste == 0:
        return prefix
    return prefix + " " + trois_chiffres(reste)


def affichage_nombre(n: int) -> str:
    """Renvoie '12 (douze)'"""
    return f"{n} ({nombre_en_lettres(n)})"


# -------------------------
# Logique du jeu
# -------------------------
class ModeleJeu:
    def __init__(self, taille=6, nb_tresors=3, nb_pieges=3, max_tentatives=15, mode="Classique", chrono=60):
        self.taille = taille
        self.nb_tresors = nb_tresors
        self.nb_pieges = nb_pieges
        self.max_tentatives = max_tentatives
        self.mode = mode
        self.chrono = chrono

        self.reset()

    def reset(self):
        self.score = 0
        self.tentatives = 0
        self.start_time = None
        self.finished = False
        self.tresors = self._generer_positions(self.nb_tresors)
        self.pieges = self._generer_positions(self.nb_pieges, exclude=self.tresors)
        self.revelees = set()

    def _generer_positions(self, nb, exclude=None):
        exclude = exclude or set()
        pos = set()
        while len(pos) < nb:
            x = random.randint(0, self.taille - 1)
            y = random.randint(0, self.taille - 1)
            if (x, y) not in exclude:
                pos.add((x, y))
        return pos

    def jouer_case(self, x, y):
        """
        Retourne:
         - 'deja' si déjà révélée
         - 'tresor' si trésor trouvé
         - 'piege' si piège
         - 'vide' si vide
         - 'victoire' si dernier trésor trouvé
         - 'perdu' si chrono expiré ou tentatives finies
        """
        if self.finished:
            return "perdu"

        if self.start_time is None:
            self.start_time = time.time()

        # Vérifier chrono si mode Chrono
        if self.mode == "Chrono":
            elapsed = time.time() - self.start_time
            if elapsed >= self.chrono:
                self.finished = True
                return "perdu"

        if (x, y) in self.revelees:
            return "deja"

        self.tentatives += 1
        self.revelees.add((x, y))

        if (x, y) in self.tresors:
            self.score += 10
            self.tresors.remove((x, y))
            if not self.tresors:
                self.finished = True
                return "victoire"
            return "tresor"

        if (x, y) in self.pieges:
            self.score = max(0, self.score - 5)
            self.pieges.remove((x, y))
            return "piege"

        # vide
        if self.mode == "Difficile":
            # pénalité légère en mode difficile pour chaque vide
            self.score = max(0, self.score - 1)
        return "vide"


# -------------------------
# Persistance des scores
# -------------------------
def charger_scores():
    if not os.path.exists(FICHIER_SCORES):
        return []
    try:
        with open(FICHIER_SCORES, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def sauvegarder_score(nom, score, mode):
    scores = charger_scores()
    scores.append({"nom": nom, "score": score, "mode": mode, "date": time.time()})
    scores = sorted(scores, key=lambda s: s["score"], reverse=True)[:50]
    try:
        with open(FICHIER_SCORES, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# -------------------------
# Interface utilisateur (Tkinter)
# -------------------------
class InterfaceChasse:
    SKINS = {
        "Classique": {
            "bg": "#1e272e", "btn_bg": "#485460", "texte": "white",
            "tresor": "#f1c40f", "piege": "#e74c3c", "vide": "#7f8fa6"
        },
        "Pirate": {
            "bg": "#2b2b2b", "btn_bg": "#6b4f3f", "texte": "#f7f1e3",
            "tresor": "#d4af37", "piege": "#8b0000", "vide": "#cfc6b8"
        },
        "Neon": {
            "bg": "#0f0f1a", "btn_bg": "#1a1a2e", "texte": "#e6fffa",
            "tresor": "#39ff14", "piege": "#ff206e", "vide": "#94b0e0"
        }
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Chasse au Trésor - Français")
        self.root.geometry("760x820")
        self.skin = "Classique"
        self.mode = "Classique"
        self.son_active = True
        self.modele = ModeleJeu()
        self.boutons = []
        self.timer_id = None

        self._construire_interface()
        self._appliquer_skin()
        self._maj_labels()

    def _construire_interface(self):
        self.root.configure(bg=self.SKINS[self.skin]["bg"])

        entete = tk.Label(self.root, text="🗺️ CHASSE AU TRÉSOR", font=("Helvetica", 20, "bold"), pady=10)
        entete.pack()

        cadre_info = tk.Frame(self.root, pady=6, bg=self.SKINS[self.skin]["bg"])
        cadre_info.pack()

        self.label_score = tk.Label(cadre_info, text="💰 " + affichage_nombre(0), font=("Helvetica", 14, "bold"))
        self.label_score.pack(side=tk.LEFT, padx=6)

        self.label_tentatives = tk.Label(cadre_info, text="🎯 " + affichage_nombre(0) + " / " + affichage_nombre(self.modele.max_tentatives),
                                         font=("Helvetica", 14, "bold"))
        self.label_tentatives.pack(side=tk.LEFT, padx=6)

        self.label_timer = tk.Label(cadre_info, text="⏱️ --:--", font=("Helvetica", 14, "bold"))
        self.label_timer.pack(side=tk.LEFT, padx=6)

        cadre_ctrl = tk.Frame(self.root, pady=8, bg=self.SKINS[self.skin]["bg"])
        cadre_ctrl.pack()

        tk.Button(cadre_ctrl, text="🔄 Nouvelle partie", command=self.nouvelle_partie, width=14).pack(side=tk.LEFT, padx=6)
        tk.Button(cadre_ctrl, text="⚙ Paramètres", command=self.ouvrir_parametres, width=12).pack(side=tk.LEFT, padx=6)
        tk.Button(cadre_ctrl, text="🏆 Meilleurs scores", command=self.afficher_scores, width=14).pack(side=tk.LEFT, padx=6)
        tk.Button(cadre_ctrl, text="❌ Quitter", command=self.root.quit, width=10).pack(side=tk.LEFT, padx=6)

        self.cadre_grille = tk.Frame(self.root, pady=14, bg=self.SKINS[self.skin]["bg"])
        self.cadre_grille.pack()

        self._creer_grille_boutons()

        self.légende = tk.Label(self.root, text="💎 Trésor (+10) | 💣 Piège (-5) | ⬜ Vide (0)", font=("Helvetica", 10))
        self.légende.pack(pady=8)

        bas = tk.Label(self.root, text="Astuce : changez le mode / skin dans Paramètres. Sons facultatifs.", font=("Helvetica", 9))
        bas.pack(pady=2)

    def _creer_grille_boutons(self):
        for child in self.cadre_grille.winfo_children():
            child.destroy()
        self.boutons = []
        taille = self.modele.taille
        for i in range(taille):
            ligne = []
            for j in range(taille):
                b = tk.Button(self.cadre_grille, text="❓", font=("Helvetica", 16, "bold"),
                              width=4, height=2, command=lambda x=i, y=j: self.clic_case(x, y))
                b.grid(row=i, column=j, padx=6, pady=6)
                ligne.append(b)
            self.boutons.append(ligne)

    def _appliquer_skin(self):
        skin = self.SKINS[self.skin]
        self.root.configure(bg=skin["bg"])
        for w in [self.label_score, self.label_tentatives, self.label_timer, self.légende]:
            w.configure(bg=skin["bg"], fg=skin["texte"])
        for row in self.boutons:
            for b in row:
                b.configure(bg=skin["btn_bg"], fg=skin["texte"], activebackground=skin["btn_bg"])
        # mise à jour de la fenêtre (remplace self.update erroné)
        self.root.update()

    def clic_case(self, x, y):
        resultat = self.modele.jouer_case(x, y)
        btn = self.boutons[x][y]

        if resultat == "deja":
            return

        if resultat == "perdu":
            self._fin_partie(perdu=True)
            return

        if resultat == "tresor":
            self._reveler_bouton(btn, "💎", self.SKINS[self.skin]["tresor"])
            self._flash(btn)
            self._jouer_son("tresor")
        elif resultat == "piege":
            self._reveler_bouton(btn, "💣", self.SKINS[self.skin]["piege"])
            self._secouer(btn)
            self._jouer_son("piege")
        elif resultat == "vide":
            self._reveler_bouton(btn, "⬜", self.SKINS[self.skin]["vide"])
        elif resultat == "victoire":
            self._reveler_bouton(btn, "💎", self.SKINS[self.skin]["tresor"])
            self._jouer_son("victoire")
            self._fin_partie(gagne=True)

        self._maj_labels()

        if self.modele.tentatives >= self.modele.max_tentatives and not self.modele.finished:
            self._fin_partie(perdu=True)

    def _reveler_bouton(self, btn, texte, couleur):
        btn.configure(text=texte, state="disabled", bg=couleur)

    def _flash(self, btn, fois=3, délai=120):
        original = btn.cget("bg")
        def step(i):
            if i >= fois:
                btn.config(bg=original)
                return
            btn.config(bg="white" if i % 2 == 0 else original)
            btn.after(délai, lambda: step(i+1))
        step(0)

    def _secouer(self, btn, fois=6, dist=6):
        info = btn.grid_info()
        r, c = info["row"], info["column"]
        orig_padx = info.get("padx", 6)
        def move(i):
            if i >= fois:
                btn.grid(row=r, column=c)
                return
            offset = (-1 if i % 2 == 0 else 1) * dist
            btn.grid(row=r, column=c, padx=orig_padx + offset)
            btn.after(45, lambda: move(i+1))
        move(0)

    def _jouer_son(self, nom):
        if not self.son_active:
            return
        if not SON_DISPONIBLE:
            return
        # placeholder: si tu veux ajouter de vrais fichiers .wav, charge-les ici.
        # pour éviter complexité, on ignore les sons détaillés.
        try:
            pass
        except Exception:
            pass

    def nouvelle_partie(self):
        # appliquer paramètres en fonction du mode sélectionné
        if self.mode == "Classique":
            self.modele = ModeleJeu(taille=6, nb_tresors=3, nb_pieges=3, max_tentatives=15, mode="Classique")
        elif self.mode == "Chrono":
            dur = simpledialog.askinteger("Chrono", "Durée du chrono en secondes :", initialvalue=60, minvalue=10, maxvalue=600)
            if dur is None:
                dur = 60
            self.modele = ModeleJeu(taille=6, nb_tresors=3, nb_pieges=3, max_tentatives=9999, mode="Chrono", chrono=dur)
        elif self.mode == "Difficile":
            self.modele = ModeleJeu(taille=7, nb_tresors=4, nb_pieges=6, max_tentatives=12, mode="Difficile")
        else:
            self.modele = ModeleJeu()

        self._creer_grille_boutons()
        self._appliquer_skin()
        self._maj_labels()
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
            self.timer_id = None
        if self.modele.mode == "Chrono":
            self._demarrer_chrono()

    def _demarrer_chrono(self):
        if self.modele.start_time is None:
            self.modele.start_time = time.time()
        def tic():
            elapsed = time.time() - (self.modele.start_time or time.time())
            restant = max(0, int(self.modele.chrono - elapsed))
            m = restant // 60
            s = restant % 60
            self.label_timer.config(text=f"⏱️ {m:02d}:{s:02d}")
            if restant <= 0:
                self._fin_partie(perdu=True)
                return
            self.timer_id = self.root.after(500, tic)
        tic()

    def _fin_partie(self, gagne=False, perdu=False):
        self.modele.finished = True
        for row in self.boutons:
            for b in row:
                b.config(state="disabled")
        if gagne:
            nom = simpledialog.askstring("Victoire !", f"Bravo ! Score : {self.modele.score}\nEntrez ton nom pour le tableau :")
            if nom:
                sauvegarder_score(nom, self.modele.score, self.modele.mode)
            messagebox.showinfo("Victoire", f"Tu as gagné ! Score : {self.modele.score}")
        elif perdu:
            messagebox.showinfo("Fin", f"Partie terminée.\nScore : {self.modele.score}")
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
            self.timer_id = None
        # Afficher aussi positions restantes (optionnel) : on les laisse cachées pour challenge

    def ouvrir_parametres(self):
        dlg = DialogueParametres(self.root, self.skin, self.mode, self.son_active)
        self.root.wait_window(dlg.top)
        if dlg.result:
            self.skin, self.mode, self.son_active = dlg.result
            self._appliquer_skin()
            self.nouvelle_partie()

    def afficher_scores(self):
        scores = charger_scores()
        if not scores:
            messagebox.showinfo("Meilleurs scores", "Aucun score enregistré.")
            return
        texte = ""
        for i, s in enumerate(scores[:15]):
            nom = s.get("nom", "Anonyme")
            pts = s.get("score", 0)
            mode = s.get("mode", "—")
            texte += f"{i+1}. {nom} — {pts} pts ({mode})\n"
        messagebox.showinfo("Meilleurs scores", texte)

    def _maj_labels(self):
        self.label_score.config(text="💰 " + affichage_nombre(self.modele.score))
        self.label_tentatives.config(
            text="🎯 " + affichage_nombre(self.modele.tentatives) + " / " + affichage_nombre(self.modele.max_tentatives)
        )
        if self.modele.mode != "Chrono":
            self.label_timer.config(text="⏱️ --:--")
        else:
            if self.timer_id is None:
                self._demarrer_chrono()


# -------------------------
# Dialogue paramètres
# -------------------------
class DialogueParametres:
    def __init__(self, parent, skin_courant, mode_courant, son_courant):
        self.top = tk.Toplevel(parent)
        self.top.title("Paramètres")
        self.top.grab_set()
        self.result = None

        tk.Label(self.top, text="Thème (skin)").pack(pady=4)
        self.var_skin = tk.StringVar(value=skin_courant)
        for s in InterfaceChasse.SKINS.keys():
            tk.Radiobutton(self.top, text=s, variable=self.var_skin, value=s).pack(anchor="w")

        tk.Label(self.top, text="Mode de jeu").pack(pady=6)
        self.var_mode = tk.StringVar(value=mode_courant)
        for m in ["Classique", "Chrono", "Difficile"]:
            tk.Radiobutton(self.top, text=m, variable=self.var_mode, value=m).pack(anchor="w")

        self.var_son = tk.BooleanVar(value=son_courant)
        tk.Checkbutton(self.top, text="Sons activés (si pygame installé)", variable=self.var_son).pack(pady=6)

        cadre_btn = tk.Frame(self.top)
        cadre_btn.pack(pady=8)
        tk.Button(cadre_btn, text="OK", command=self.ok).pack(side=tk.LEFT, padx=6)
        tk.Button(cadre_btn, text="Annuler", command=self.annuler).pack(side=tk.LEFT, padx=6)

    def ok(self):
        self.result = (self.var_skin.get(), self.var_mode.get(), self.var_son.get())
        self.top.destroy()

    def annuler(self):
        self.top.destroy()


# -------------------------
# Lancement de l'application
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceChasse(root)
    root.mainloop()
