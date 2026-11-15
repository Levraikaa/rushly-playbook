"""Synthèse fusionnée par créateur, écrite dans data.json.

Chaque idée : [verdict, idée, détail, ce que ça donne pour Rushly, [[videoId, secondes], ...]]
Une idée citée dans plusieurs vidéos = une idée qui revient.
Une idée ajoutée plus tard porte "ajoute": "JJ/MM/AAAA" pour afficher la bulle New.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

COURT = {
    "wQnBj8u15Es": "400 M de vues", "LCPapr3UHic": "Stratégie 2026", "QHknYmt0Zsw": "3 M€ grâce à TikTok",
    "aKr-s1r0msg": "Formation 5 000 €", "NERMtIf3tss": "Personal brand",
    "XEq7F-QLslA": "Comprendre l'acquisition", "dBoDDcCpZ_8": "Acquisition simple", "yYMwsA7HBHQ": "Tier list des canaux",
    "Yfov2rLbT5o": "1 M€ (encore)", "k4bTkNe2PDo": "Personne ne veut de ton SaaS", "vzgBHo5D0lo": "Dominer ton marché",
    "wXG4hk_Jjgs": "7 habitudes", "RWUduvp6i_c": "Remakeit à 800 k€", "rAu4G4mGtNA": "3 M€ en interview",
    "PN5v0cRY_Dk": "Voler du contenu", "fWIbNYyk_KE": "TikTok en 20 jours",
}

LEO = [
    ("Piloter l'acquisition", [
        ["ok", "Le RPM est la seule métrique", "Cash encaissé ÷ vues × 1 000. Un SaaS sain fait 2 à 5 € dès le jour 1. 1 M de vues ≈ 5 k€ de MRR en moyenne, selon lui.", "Calculer le RPM du compte Rushly.", [["XEq7F-QLslA", 190], ["dBoDDcCpZ_8", 46]]],
        ["ok", "Percer seul avant de recruter", "Pas de créateurs tant que ton propre compte n'a pas rapporté 3 à 5 k€. Il faut 500 000 à 1 M de vues pour un RPM fiable.", "Compte Rushly d'abord, créateurs ensuite.", [["XEq7F-QLslA", 478]]],
        ["ok", "Mesurer chaque étape du funnel", "Combien convertissent, où ça décroche, conversion du paywall. Remakeit suit aussi le % de vidéos générées qui ratent.", "Suivre le % de rushs qui sortent en vidéo publiable.", [["vzgBHo5D0lo", 330], ["RWUduvp6i_c", 238], ["rAu4G4mGtNA", 2045]]],
        ["ok", "Ne rien juger trop tôt", "Minimum 5 à 10 jours et 5 vidéos qui percent avant de conclure. Tenir 30 jours : un compte peut décoller d'un coup.", "30 vidéos avant de juger le compte Rushly.", [["wXG4hk_Jjgs", 520], ["PN5v0cRY_Dk", 423], ["dBoDDcCpZ_8", 46]]],
    ]),
    ("Faire le contenu", [
        ["ok", "Le SaaS est le moyen, jamais le sujet", "Une vidéo qui parle de l'app ne fait ni vues ni ventes. Plus ça ressemble à de la vente, moins ça vend, surtout en France.", "Parler de « poster sans monter », Rushly arrive dans le process.", [["dBoDDcCpZ_8", 237], ["k4bTkNe2PDo", 47]]],
        ["ok", "Le hook fait 60 % de la viralité", "Rétention 30 %, montage 10 %. Le hook promet un résultat (sujet + résultat) sans nommer l'outil.", "", [["dBoDDcCpZ_8", 0], ["k4bTkNe2PDo", 142]]],
        ["ok", "Garder le format, changer le hook", "On n'innove pas sur le format. Une vidéo qui marche est déclinée en hooks. 80 % sur ce qui marche, 10 à 20 % de tests.", "Dès qu'une vidéo perce : 5 hooks différents sur le même corps.", [["dBoDDcCpZ_8", 0], ["wXG4hk_Jjgs", 331], ["rAu4G4mGtNA", 1759]]],
        ["ok", "Montrer le résultat, paywall juste avant", "Le viewer a 10 secondes : montre le résultat, pas les fonctions. Le paywall arrive juste avant ce résultat. La vidéo ne vend pas, c'est le parcours qui vend.", "Montrer le rush brut puis la vidéo montée.", [["k4bTkNe2PDo", 237], ["k4bTkNe2PDo", 285], ["rAu4G4mGtNA", 2660]]],
        ["ok", "Révéler l'outil petit à petit", "Un process en étapes, l'outil arrive tard : l'envie monte.", "Rushly n'apparaît qu'à l'étape du montage.", [["k4bTkNe2PDo", 334]]],
        ["ok", "Un rush viral, 10 montages", "Un rush qui a percé, remonté par 10 personnes, donne 10 vidéos virales. Jamais de repost à l'identique.", "C'est le produit : le même rush monté en 5 styles.", [["XEq7F-QLslA", 668], ["XEq7F-QLslA", 622]]],
        ["ok", "4 formats qui marchent", "Le flow du logiciel filmé au téléphone, le duo, le talking head (convertit le mieux), le green screen sur l'actu.", "", [["dBoDDcCpZ_8", 284], ["dBoDDcCpZ_8", 332]]],
        ["ok", "3 règles d'exécution", "Filmer l'écran avec un autre appareil, produit visible avant 20 s, nom du produit jamais dans le texte, le titre ou la description.", "", [["dBoDDcCpZ_8", 380]]],
        ["ok", "Sourcer les formats ailleurs", "80 à 90 % de leurs formats viennent des US ou d'autres niches. Se faire une banque de 100 formats.", "Banque de formats de créateurs face cam US et FR.", [["dBoDDcCpZ_8", 141], ["wXG4hk_Jjgs", 378]]],
        ["ok", "Copier et faire mieux", "Reprendre un concept qui marche en le battant sur 2 ou 3 points. Décortiquer les 10 meilleurs scripts.", "", [["PN5v0cRY_Dk", 47], ["PN5v0cRY_Dk", 187]]],
        ["ok", "1 vidéo par jour au démarrage", "Plusieurs vidéos par jour sur un compte neuf passent pour du spam.", "", [["PN5v0cRY_Dk", 329], ["dBoDDcCpZ_8", 46]]],
        ["ok", "Une seule niche par compte", "Une vidéo hors niche casse la dynamique. Une vidéo qui perce relance les anciennes.", "", [["fWIbNYyk_KE", 286], ["fWIbNYyk_KE", 334]]],
        ["ok", "Seuils de rétention", "Plus de 20 s de visionnage moyen et au moins 15 % d'achèvement, sinon la vidéo ne décolle pas, selon lui.", "Sous 15 % d'achèvement à 24 h, retravailler le hook.", [["fWIbNYyk_KE", 237]]],
        ["ok", "Lire les commentaires des vidéos qui percent", "Les questions posées donnent les prochains angles.", "", [["wXG4hk_Jjgs", 473]]],
        ["ok", "Le défi documenté", "Un objectif chiffré suivi jour par jour, l'outil apparaît comme ce qu'on utilise.", "", [["fWIbNYyk_KE", 0]]],
    ]),
    ("Les canaux", [
        ["ok", "Au lancement : clipping, créateurs, affiliation", "Clipping et créateurs sur comptes dédiés en tier S (50 à 80 % de son acquisition), affiliation en tier A. Influenceurs plus tard. Cold email, webinaire, SEO en C.", "", [["yYMwsA7HBHQ", 94], ["yYMwsA7HBHQ", 188], ["yYMwsA7HBHQ", 524], ["yYMwsA7HBHQ", 808]]],
        ["ok", "Payer à la performance", "90 % de leur acquisition. Paiement à la vue, par palier ou en affiliation, avec un CPM sous le RPM.", "Barème Whop calé sur le RPM mesuré.", [["XEq7F-QLslA", 238], ["dBoDDcCpZ_8", 569]]],
        ["ok", "Pas d'ads avant 50 à 100 k€ de MRR", "Et jamais plus de 5 % de l'acquisition.", "", [["XEq7F-QLslA", 96], ["dBoDDcCpZ_8", 569]]],
        ["ok", "Le clipping a cassé le plafond", "Remakeit bloqué à 60 k€ de MRR pendant 4 à 5 mois, puis 200 k€ avec le clipping et les créateurs en masse, selon lui.", "Préparer le relais créateurs avant le plafond du compte Rushly.", [["Yfov2rLbT5o", 94]]],
        ["ok", "Des créateurs qui ressemblent à la cible", "Plus de créateurs plutôt que plus de budget. Des créateurs hors cible donnent un mauvais RPM.", "Recruter des créateurs face cam qui ne montent pas.", [["XEq7F-QLslA", 96], ["XEq7F-QLslA", 334]]],
        ["ok", "Recruter dans une vidéo qui perce", "Un appel « deviens clipper » dans une vidéo virale a ramené 600 candidats. Ils gagnent plus qu'avec la monétisation TikTok.", "Même appel dans la vidéo Rushly qui perce.", [["rAu4G4mGtNA", 1950], ["rAu4G4mGtNA", 2472]]],
        ["ok", "L'outil se promeut avec l'outil", "Les créateurs utilisent Remakeit pour faire les vidéos qui promeuvent Remakeit.", "Les vidéos des créateurs sont montées avec Rushly.", [["RWUduvp6i_c", 428], ["RWUduvp6i_c", 475]]],
        ["ok", "Les gens cherchent le nom", "Le trafic arrive sur Remakeit sans passer par le lien en bio, selon lui.", "« Rushly » facile à taper et à trouver.", [["Yfov2rLbT5o", 572]]],
        ["ok", "Affiliation : dashboard soigné", "Gros pourcentage sur le 1er mois ou à vie, et un dashboard stylé pour les affiliés.", "", [["yYMwsA7HBHQ", 524]]],
    ]),
    ("Le produit", [
        ["ok", "Audience large, produit centré", "Le produit se concentre sur une étape. L'audience reste large, la data dit quel profil convertit.", "Rushly = du rush à la vidéo publiable.", [["vzgBHo5D0lo", 46], ["vzgBHo5D0lo", 140]]],
        ["ok", "Moins d'options", "Les gens ne veulent pas d'options ni d'innovation qu'ils ne comprennent pas.", "Un style recommandé par défaut.", [["rAu4G4mGtNA", 2613]]],
        ["ok", "Premiers clients dans une communauté", "MVP vendu à une audience déjà chaude, puis chaque utilisateur appelé un par un.", "Appeler les premiers payants Rushly.", [["RWUduvp6i_c", 285], ["RWUduvp6i_c", 380]]],
        ["ok", "L'avantage, c'est la distribution", "Le produit se copie vite. Moins de 20 % du temps sur le produit, le reste sur l'acquisition.", "", [["vzgBHo5D0lo", 518], ["wXG4hk_Jjgs", 236]]],
        ["ok", "Une infra qui tient le jour J", "Un lancement qui bugue tue la hype de la première vidéo virale.", "Tester la charge avant le 10/11.", [["rAu4G4mGtNA", 423]]],
    ]),
]

ROBIN = [
    ("Trouver les formats", [
        ["ok", "Le format compte plus que le volume", "80 % de leurs vues viennent de 10 créateurs sur des formats prouvés.", "", [["wQnBj8u15Es", 0], ["wQnBj8u15Es", 47]]],
        ["ok", "Un format est validé quand il perce plusieurs fois", "Au moins 3 fois à plus de 100 000 vues, sur les 90 derniers jours. Une vidéo virale est très au-dessus de la moyenne du créateur.", "", [["wQnBj8u15Es", 575], ["wQnBj8u15Es", 863], ["LCPapr3UHic", 478]]],
        ["ok", "Repérer les vidéos boostées", "Likes au-dessus de 2 % des vues = organique. En dessous, souvent poussée en ads.", "", [["wQnBj8u15Es", 1195]]],
        ["ok", "Chercher large", "Plusieurs couches (concurrents, niche, formats universels), plusieurs mots-clés, en anglais, sur X avec un minimum de likes, et dans les autres pays.", "Créateurs face cam US et FR.", [["wQnBj8u15Es", 479], ["LCPapr3UHic", 335], ["QHknYmt0Zsw", 1766]]],
        ["ok", "Un avatar précis et un compte neuf", "Une seule personne en tête. Un compte TikTok neuf où on ne like que la niche montre le feed de la cible.", "", [["NERMtIf3tss", 1776], ["NERMtIf3tss", 478], ["LCPapr3UHic", 94]]],
    ]),
    ("Faire le contenu", [
        ["ok", "Le produit est une étape, jamais une pub", "On montre une méthode en étapes, le produit est l'une d'elles.", "Rushly montré comme l'étape du montage.", [["wQnBj8u15Es", 767], ["LCPapr3UHic", 1100], ["LCPapr3UHic", 1241], ["QHknYmt0Zsw", 574]]],
        ["ok", "Le hook à contre-pied", "Dire ce que la cible n'a pas l'habitude d'entendre, puis le justifier.", "", [["LCPapr3UHic", 141], ["NERMtIf3tss", 382], ["NERMtIf3tss", 1532]]],
        ["ok", "Copier ne suffit pas", "Les 5 % qu'on oublie, souvent le hook visuel, sont ce qui rendait la vidéo virale. Un mauvais hook tue la rétention.", "", [["aKr-s1r0msg", 5636], ["aKr-s1r0msg", 8778], ["QHknYmt0Zsw", 2005]]],
        ["ok", "Question-réponse et carrousel", "Le question-réponse a le meilleur ratio temps / vues pour démarrer. Le carrousel TikTok : forte demande, peu d'offre.", "", [["LCPapr3UHic", 816], ["LCPapr3UHic", 910]]],
        ["ok", "Un produit qui fait « waouh » à l'écran", "L'animation ou l'interface est virale en elle-même.", "Le passage du rush brut au rendu doit claquer.", [["wQnBj8u15Es", 336]]],
        ["warn", "Positionnement en 5 mots, plus une polémique", "", "« Le rendu d'un monteur, sans monteur. »", [["wQnBj8u15Es", 239]]],
        ["ok", "Une méthode qui différencie", "Mettre en avant un élément précis que personne ne met en avant.", "Les styles plutôt que « montage IA ».", [["NERMtIf3tss", 1582]]],
        ["ok", "Parler sans lire de script", "Hook, 3 points, conclusion, le reste en improvisé.", "", [["NERMtIf3tss", 1242]]],
    ]),
    ("Le rythme", [
        ["ok", "1 vidéo par jour, faite le jour même", "Pour ajuster selon ce qui a marché la veille.", "", [["LCPapr3UHic", 1337]]],
        ["ok", "70 % de reprises, 30 % de tests", "", "", [["QHknYmt0Zsw", 811]]],
        ["ok", "Un winner se refait des dizaines de fois", "25 à 50 fois, avec des variantes. Chaque semaine, chercher de nouvelles variantes des formats gagnants.", "", [["LCPapr3UHic", 1479], ["wQnBj8u15Es", 1484]]],
    ]),
    ("Convertir et amplifier", [
        ["ok", "Mot-clé en commentaire, message privé automatique", "La ressource envoyée prolonge le sujet de la vidéo et finit par un appel à l'action.", "Le lead magnet de Rushly.", [["aKr-s1r0msg", 19028], ["aKr-s1r0msg", 16269]]],
        ["ok", "Le plafond se casse par la conversion", "Remakeit a doublé ses vues sans croître pendant 5 mois. Débloqué par des tests de prix et de paywall.", "", [["QHknYmt0Zsw", 1435], ["QHknYmt0Zsw", 1483]]],
        ["warn", "Créateurs et clippers payés à la vue", "1 $ les 1 000 vues chez Robin. Clipping via Whop, influenceurs au RPM.", "Après un winner et un RPM mesuré.", [["LCPapr3UHic", 1620], ["QHknYmt0Zsw", 526]]],
        ["warn", "Stories et lives", "Pour convertir les abonnés une fois qu'il y en a.", "Plus tard.", [["aKr-s1r0msg", 18883]]],
    ]),
]

TOP = {
    "leo-grindarss": [
        ["Le SaaS est le moyen, jamais le sujet", "Une vidéo qui parle de l'app ne vend pas. On parle d'un sujet, l'outil arrive dans le process."],
        ["Le hook fait 60 % de la viralité", "Il promet un résultat, sans nommer l'outil."],
        ["Garder le format, changer le hook", "Une vidéo qui marche se décline en hooks. 80 % sur ce qui marche, le reste en tests."],
        ["Percer seul avant de recruter", "Pas de créateurs tant que ton compte n'a pas rapporté 3 à 5 k€."],
        ["Au lancement : clipping, créateurs, affiliation", "Le reste (influenceurs, ads, SEO) vient plus tard."],
        ["Payer à la performance", "Payer les créateurs à la vue, moins que ce qu'une vue te rapporte (RPM)."],
        ["Ne rien juger trop tôt", "Au moins 5 vidéos qui percent ou 30 jours avant de conclure."],
    ],
    "robin-dormion": [
        ["Le format compte plus que le volume", "80 % de leurs vues viennent de 10 créateurs sur des formats prouvés."],
        ["Un format est validé quand il perce plusieurs fois", "Au moins 3 fois à plus de 100 000 vues, sur les 90 derniers jours."],
        ["Le produit est une étape, jamais une pub", "On montre une méthode, le produit est l'une des étapes."],
        ["Le hook à contre-pied", "Dire ce que la cible n'a pas l'habitude d'entendre, puis le justifier."],
        ["Un winner se refait des dizaines de fois", "25 à 50 fois, avec des variantes de hook."],
        ["Mot-clé en commentaire, message privé automatique", "La ressource envoyée prolonge la vidéo et finit par un appel à l'action."],
        ["Le plafond se casse par la conversion", "Quand ça stagne, on teste les prix et le paywall, pas plus de vues."],
    ],
}

d = json.loads((HERE / "data.json").read_text())
d["courts"] = COURT
for c in d["createurs"]:
    src = LEO if c["id"] == "leo-grindarss" else ROBIN
    c["synthese"] = [{"theme": t, "idees": items} for t, items in src]
    c["top"] = TOP[c["id"]]
(HERE / "data.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
print("ok", {c["id"]: sum(len(t["idees"]) for t in c["synthese"]) for c in d["createurs"]})
