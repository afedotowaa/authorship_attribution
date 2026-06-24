# -*- coding: utf-8 -*-
"""Пересчёт метрик на исправленных ошибках: матрица 2x2 (фичи x разбиение).

Зачем этот файл.
---------------
В ноутбуках репозитория каждая книга заранее режется на последовательные 40k-срезы
(см. enable_threshold.py), и каждый срез становится отдельной строкой обучающей выборки.
Затем строки делятся СЛУЧАЙНО (train_test_split / cross_val_score(cv=int) / KFold(shuffle=True)),
БЕЗ передачи groups= и без GroupKFold/GroupShuffleSplit. Из-за этого смежные срезы ОДНОГО
романа попадают одновременно и в train, и в test: модель "узнаёт" конкретную книгу
(вокабуляр, темы, имена персонажей), а не авторский стиль - это утечка данных.

Здесь я считаю признаки ровно как get_features.py (полные списки ключей берём из него же),
но сохраняем id книги-источника каждого фрагмента и сравниваем ДВА независимых эффекта:

  - фичи: "как есть" (uni_keys без 'й'/'ы'/'ё'; normalize() - per-row min-max по ВСЕМУ
          гетерогенному вектору) vs "исправленные" (полный алфавит 33; нормировка ПОБЛОЧНО,
          каждое семейство признаков своим min-max);
  - разбиение: случайный сплит фрагментов (их протокол) vs группировка по книге (leak-free).

Получаются 4 ячейки: как есть -> только фикс фич -> только фикс утечки -> всё исправлено.
Классификатор - их LinearSVC(C=1, tol=1e-5).

Воспроизводимость.
-----------------
pymorphy2 НЕ запускается на Python >= 3.11 (внутри он зовёт удалённую inspect.getargspec).
Поэтому используем API-совместимый pymorphy3 на тех же словарях OpenCorpora.

Данные.
-------
Нужен корпус ИСХОДНЫХ книг (до резки): раскладка <AA_CORPUS>/<автор>/<книга>.txt, у автора >= 2 книг.
Путь задаётся переменной окружения AA_CORPUS. Прочие параметры: AA_WIN, AA_AUTHORS, AA_CAP, AA_ROUNDS.
    pip install pymorphy3 scikit-learn numpy
    AA_CORPUS=/path/to/corpus python evaluation_leakfree.py
"""
from __future__ import annotations
import os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
import re
import ast as _ast
import json
import pathlib
import random
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pymorphy3                 # вместо pymorphy2 - он не работает на Python >= 3.11
from sklearn.svm import LinearSVC

HERE = pathlib.Path(__file__).parent
CORPUS = pathlib.Path(os.environ.get("AA_CORPUS", str(HERE)))
WIN = int(os.environ.get("AA_WIN", "15000"))            # длина фрагмента (символов)
MAX_AUTHORS = int(os.environ.get("AA_AUTHORS", "40"))   # сколько авторов взять
CAP = int(os.environ.get("AA_CAP", "8"))                # фрагментов на автора
ROUNDS = int(os.environ.get("AA_ROUNDS", "12"))         # повторов случайного отбора 3+1
RNG = random.Random(42)
MORPH = pymorphy3.MorphAnalyzer()
_WORD = re.compile(r"(^[^a-zA-Zа-яёА-ЯЁ\d]+)|([^a-zA-Zа-яёА-ЯЁ\d]+$)")
_norm, _pos = {}, {}


def _load_keys():
    """ читаем 6 списков ключей (sharov/uni/pos/punct/tri/bigr) прямо из get_features.py """
    src = (HERE / "get_features.py").read_text("utf-8")
    out = {}
    for name in ("sharov_keys", "uni_keys", "pos_keys", "punct_keys", "tri_keys", "bigr_keys"):
        i = src.index("\n" + name); j = src.index("[", i); depth = 0
        for k in range(j, len(src)):
            if src[k] == "[":
                depth += 1
            elif src[k] == "]":
                depth -= 1
                if depth == 0:
                    end = k + 1; break
        out[name] = _ast.literal_eval(src[j:end])
    return out


_K = _load_keys()
PUNCT = sorted(_K["punct_keys"]); POSK = sorted(_K["pos_keys"])
BIGR = sorted(_K["bigr_keys"]); TRI = sorted(_K["tri_keys"]); SHAROV = _K["sharov_keys"]
# Алфавиты задаём ЯВНО, чтобы "как есть" воспроизводилось независимо от того, что в get_features.py
# uni_keys уже могли поправить: BUGGY - исходные 30 букв (без 'й','ы','ё'), FIXED - полные 33.
UNI_BUGGY = sorted(['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к', 'л', 'м', 'н', 'о', 'п',
                    'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'щ', 'ш', 'ъ', 'ь', 'э', 'ю', 'я'])
UNI_FIXED = sorted(set(UNI_BUGGY) | {"й", "ы", "ё"})           # полный алфавит 33


def words(t):
    return tuple(w for w in (_WORD.sub("", x) for x in t.split()) if w)


def nf(w):
    v = _norm.get(w)
    if v is None:
        v = MORPH.parse(w)[0].normal_form; _norm[w] = v
    return v


def pos(w):
    v = _pos.get(w)
    if v is None:
        v = MORPH.parse(w)[0].tag.POS; _pos[w] = v
    return v


def mm(block):
    """ их формула (x-min)/(max-min) по переданному списку (с защитой от деления на 0) """
    lo, hi = min(block), max(block); rng = (hi - lo) or 1e-9
    return [(x - lo) / rng for x in block]


def blocks(text):
    text = text.lower(); ws = words(text)
    if not ws:
        return None
    nws = [nf(w) for w in ws]; nl = len(nws) or 1; tl = len(text) or 1
    poss = [pos(w) for w in ws]; pl = len(poss) or 1
    return dict(
        punct=[text.count(c) / tl for c in PUNCT],
        pos=[poss.count(p) / pl for p in POSK],
        bigr=[text.count(c) / tl for c in BIGR],
        tri=[text.count(c) / tl for c in TRI],
        sharov=[nws.count(w) / nl for w in SHAROV],
        uni_b=[text.count(c) / tl for c in UNI_BUGGY],
        uni_f=[text.count(c) / tl for c in UNI_FIXED],
    )


def vec_buggy(b):
    """ как у них: один per-row min-max по всему конкатенированному вектору """
    data = b["punct"] + b["pos"] + b["uni_b"] + b["bigr"] + b["tri"] + b["sharov"]
    return mm(data)


def vec_fixed(b):
    """ фикс: полный алфавит + ПОБЛОЧНАЯ нормировка (каждое семейство своим min-max) """
    return mm(b["punct"]) + mm(b["pos"]) + mm(b["uni_f"]) + mm(b["bigr"]) + mm(b["tri"]) + mm(b["sharov"])


def load_pool():
    pool = {}
    for adir in sorted(p for p in CORPUS.iterdir() if p.is_dir()):
        files = sorted(adir.glob("*.txt"))
        if len(files) < 2:
            continue
        bb = []
        for bi, f in enumerate(files):
            t = f.read_text("utf-8", "ignore")
            w = [t[i:i + WIN] for i in range(0, len(t) - WIN + 1, WIN)]
            if w:
                bb.append((bi, w))
        if len(bb) < 2:
            continue
        frs, ptr = [], {bi: 0 for bi, _ in bb}
        while len(frs) < CAP:
            adv = False
            for bi, w in bb:
                if ptr[bi] < len(w) and len(frs) < CAP:
                    frs.append((bi, w[ptr[bi]])); ptr[bi] += 1; adv = True
            if not adv:
                break
        if len({b for b, _ in frs}) >= 2 and len(frs) >= 4:
            pool[adir.name] = frs
        if len(pool) >= MAX_AUTHORS:
            break
    return pool


def cv(X, y, books, authors, grouped):
    """ 3 train + 1 test фрагмента на автора. grouped=True => test из книги, которой нет в train. """
    iba = {a: [i for i in range(len(y)) if y[i] == a] for a in authors}
    accs = []
    for _ in range(ROUNDS):
        tr, te, ok = [], [], True
        for a in authors:
            idx = iba[a][:]; RNG.shuffle(idx)
            if grouped:
                uq = list(dict.fromkeys(books[i] for i in idx))
                if len(uq) < 2:
                    ok = False; break
                tb = uq[0]
                tp = [i for i in idx if books[i] == tb]
                trp = [i for i in idx if books[i] != tb]
                if len(trp) < 3 or not tp:
                    ok = False; break
                tr += trp[:3]; te += [tp[0]]
            else:
                if len(idx) < 4:
                    ok = False; break
                tr += idx[:3]; te += [idx[3]]
        if not ok:
            continue
        clf = LinearSVC(C=1.0, tol=1e-5).fit(X[tr], [y[i] for i in tr])
        p = clf.predict(X[te])
        accs.append(np.mean([p[k] == y[te[k]] for k in range(len(te))]))
    return float(np.mean(accs)) if accs else float("nan")


def main():
    if not CORPUS.exists():
        print(f"нет корпуса: {CORPUS} (задайте AA_CORPUS=<путь к <автор>/<книга>.txt>)"); return
    print(f"корпус: {CORPUS}", flush=True)
    print(f"фичеризация (признаки get_features.py, pymorphy3), <= {MAX_AUTHORS} авт. с >= 2 книгами...", flush=True)
    pool = load_pool()
    Xb, Xf, y, books = [], [], [], []
    for a, frs in pool.items():
        for bi, t in frs:
            b = blocks(t)
            if b is None:
                continue
            Xb.append(vec_buggy(b)); Xf.append(vec_fixed(b)); y.append(a); books.append("%s#%d" % (a, bi))
    Xb = np.array(Xb, np.float32); Xf = np.array(Xf, np.float32)
    authors = sorted(set(y))
    print("готово: %d авт., %d фрагм. | признаков: как есть %d, исправл. %d\n"
          % (len(authors), len(Xb), Xb.shape[1], Xf.shape[1]), flush=True)

    cells = {
        "as_is      (фичи как есть · случайный сплит)": cv(Xb, y, books, authors, False),
        "leak_fixed (фичи как есть · группировка по книге)": cv(Xb, y, books, authors, True),
        "feat_fixed (исправл. фичи · случайный сплит)": cv(Xf, y, books, authors, False),
        "all_fixed  (исправл. фичи · группировка по книге)": cv(Xf, y, books, authors, True),
    }
    print("=== матрица 2x2, %d авторов, их LinearSVC, 3 train + 1 test ===" % len(authors), flush=True)
    for k, v in cells.items():
        print("  %s: %.3f" % (k, v), flush=True)
    print(flush=True)
    feat_gain = (cells[list(cells)[2]] - cells[list(cells)[0]]) * 100
    leak_prem = (cells[list(cells)[2]] - cells[list(cells)[3]]) * 100
    print("  фикс ТОЛЬКО фич:    случайный %.3f -> %.3f (%+.1f п.п.) - их normalize() калечит их же признаки"
          % (cells[list(cells)[0]], cells[list(cells)[2]], feat_gain), flush=True)
    print("  фикс ТОЛЬКО утечки: на исправл. фичах %.3f -> %.3f (премия утечки %+.1f п.п.)"
          % (cells[list(cells)[2]], cells[list(cells)[3]], leak_prem), flush=True)
    print("  ИТОГ (всё исправлено, leak-free): %.3f" % cells[list(cells)[3]], flush=True)
    print("  (премия утечки шумна на малых выборках; устойчивая оценка - на 40+ авторах)", flush=True)

    out = {"n_authors": len(authors), "n_fragments": len(Xb), "win_chars": WIN,
           "cells": {k.split()[0]: round(v, 3) for k, v in cells.items()}}
    (HERE / "evaluation_leakfree_result.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), "utf-8")


if __name__ == "__main__":
    main()
