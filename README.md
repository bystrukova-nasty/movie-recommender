# Movie Recommender System

## Описание проекта

Проект представляет собой рекомендательную систему фильмов на основе оценок пользователей.

Для построения рекомендаций использовалась модель Collaborative Filtering с алгоритмом Matrix Factorization (SVD) из библиотеки Surprise.

Датасет: MovieLens Latest Small.

---

## Используемые технологии

* Python
* Pandas
* NumPy
* Scikit-Surprise
* Matplotlib
* Weights & Biases
* Joblib

---

## Структура проекта

* Movie_Recommendation.ipynb — основной ноутбук
* best_model.pkl — сохраненная модель
* requirements.txt — зависимости проекта

---

## Запуск проекта

Установить зависимости:

pip install -r requirements.txt

Запустить ноутбук:

Movie_Recommendation.ipynb

---

## Результаты

Проведены эксперименты с различными гиперпараметрами модели SVD.

Лучшая модель:

* n_factors = 50
* n_epochs = 20

Метрика:

RMSE = 0.877468

---

## Инференс

В конце ноутбука реализован пример загрузки модели и получения предсказания рейтинга для нового пользователя и фильма.
