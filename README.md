# Bitpin Project

## Description

A Django application using Django Rest Framework (DRF) where users can view a list of articles and rate them. The application handles high-performance requirements and includes mechanisms to mitigate the impact of unrealistic and emotional ratings.

## Features

- Display a list of articles with title, number of ratings, and average rating.
- Submit and update ratings for articles.
- Mechanism to handle unrealistic and emotional ratings.
- Performance tested for handling a large number of ratings.

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd bitpin_project
    chmod +x entrypoint.sh
    ```

2. Create a `.env` file with the following content:
    ```env
    POSTGRES_DB=bitpin_db
    POSTGRES_USER=bitpin_user
    POSTGRES_PASSWORD=bitpin_password
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    REDIS_URL=redis://redis:6379/0
    SECRET_KEY=your_secret_key
    ```

3. Build and start the Docker containers:
    ```sh
    docker-compose up --build
    ```

4. Apply migrations and create a superuser:
    ```sh
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

5. Access the application at `http://localhost:8000`.

## Running Tests

To run the tests, execute the following command:
    ```sh
    docker-compose exec web python manage.py test
    ```

## Performance Mechanism

To mitigate the impact of unrealistic and emotional ratings, the application uses a background task system (Celery) with the following steps:

1. **Accumulate Ratings**: When a user submits a rating, instead of updating the article's rating statistics immediately, the rating is stored in an `AccumulatedRating` model. This allows the system to gather a batch of ratings over a short period.

2. **Process Ratings**: Every 10 minutes, a Celery task processes these accumulated ratings. This task first identifies which articles have ratings to be processed. For each article, it calculates the average and standard deviation of the scores.

3. **Filter Ratings**: Using the calculated average and standard deviation, the task computes the Z-score for each rating. Ratings with a Z-score greater than 2 (considered outliers) are filtered out to remove the impact of extreme ratings.

4. **Update Statistics**: The filtered ratings are then used to update the article's statistics. This ensures that only ratings within a reasonable range affect the article's overall rating. After updating the statistics, the accumulated ratings are deleted.

This mechanism ensures that short-term events, such as a sudden influx of emotional ratings from a highly engaged Telegram channel, do not have a lasting impact on the article's score.

---

# پروژه بیت‌پین

## توضیحات

یک برنامه جنگو با استفاده از Django Rest Framework (DRF) که کاربران می‌توانند لیست مقالات را مشاهده کرده و به آنها امتیاز دهند. این برنامه نیازهای عملکرد بالا را مدیریت می‌کند و شامل مکانیسم‌هایی برای کاهش تأثیر امتیازات غیرواقعی و احساسی است.

## ویژگی‌ها

- نمایش لیست مقالات با عنوان، تعداد امتیازات و میانگین امتیاز.
- ارسال و به‌روزرسانی امتیازات برای مقالات.
- مکانیسمی برای مدیریت امتیازات غیرواقعی و احساسی.
- تست عملکرد برای مدیریت تعداد زیادی امتیاز.

## پیش‌نیازها

- Docker
- Docker Compose

## راه‌اندازی

1. مخزن را کلون کنید:
    ```sh
    git clone <repository-url>
    cd bitpin_project
    chmod +x entrypoint.sh
    ```

2. یک فایل `.env` با محتوای زیر ایجاد کنید:
    ```env
    POSTGRES_DB=bitpin_db
    POSTGRES_USER=bitpin_user
    POSTGRES_PASSWORD=bitpin_password
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    REDIS_URL=redis://redis:6379/0
    SECRET_KEY=your_secret_key
    ```

3. کانتینرهای Docker را بسازید و شروع کنید:
    ```sh
    docker-compose up --build
    ```

4. مایگریشن‌ها را اعمال کنید و یک کاربر ابرایجاد کنید:
    ```sh
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

5. به برنامه در `http://localhost:8000` دسترسی پیدا کنید.

## اجرای تست‌ها

برای اجرای تست‌ها، فرمان زیر را اجرا کنید:
    ```sh
    docker-compose exec web python manage.py test
    ```


## مکانیسم عملکرد

برای کاهش تأثیر امتیازات غیرواقعی و احساسی، برنامه از یک سیستم وظایف پس‌زمینه (Celery) با مراحل زیر استفاده می‌کند:

1. **جمع‌آوری امتیازات**: وقتی یک کاربر امتیازی ارسال می‌کند، به جای اینکه بلافاصله آمار امتیازات مقاله به‌روزرسانی شود، امتیاز در مدل `AccumulatedRating` ذخیره می‌شود. این اجازه می‌دهد سیستم در یک بازه زمانی کوتاه، مجموعه‌ای از امتیازات را جمع‌آوری کند.

2. **پردازش امتیازات**: هر 10 دقیقه، یک وظیفه Celery این امتیازات جمع‌آوری‌شده را پردازش می‌کند. این وظیفه ابتدا مقالاتی را که امتیازاتی برای پردازش دارند شناسایی می‌کند. برای هر مقاله، میانگین و انحراف معیار امتیازات محاسبه می‌شود.

3. **فیلتر کردن امتیازات**: با استفاده از میانگین و انحراف معیار محاسبه‌شده، وظیفه نمره Z را برای هر امتیاز محاسبه می‌کند. امتیازاتی که نمره Z آنها بیشتر از 2 باشد (در نظر گرفته می‌شوند که بیرون از محدوده عادی هستند) فیلتر می‌شوند تا تأثیر امتیازات شدید حذف شود.

4. **به‌روزرسانی آمار**: امتیازات فیلترشده سپس برای به‌روزرسانی آمار مقاله استفاده می‌شوند. این تضمین می‌کند که تنها امتیازات در محدوده معقول بر امتیاز کلی مقاله تأثیر می‌گذارند. پس از به‌روزرسانی آمار، امتیازات جمع‌آوری‌شده حذف می‌شوند.

این مکانیسم تضمین می‌کند که رویدادهای کوتاه‌مدت، مانند هجوم ناگهانی امتیازات احساسی از یک کانال تلگرام پرجنب‌وجوش، تأثیر ماندگاری بر امتیاز مقاله ندارند.

