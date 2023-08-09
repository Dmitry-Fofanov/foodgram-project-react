username: admin

password: admin

@address: [foodgram.onthewifi.com](foodgram.onthewifi.com)

# Foodgram Project

## Description

A recipe blog website where you can post recipes, track your favourites and your shopping cart.

## Local Launch

### Prerequisites

To launch this project you need a terminal with git and docker installed.

### Instruction

1. Clone the repository.

```bash
git clone https://github.com/Dmitry-Fofanov/foodgram-project-react.git
```

2. Enter the project folder.

```bash
cd foodgram-project-react
```

3. Create and start containers.

```
docker compose up
```

4. The project will now be available at [localhost](localhost).

You can also access the admin panel at [localhost/admin/](localhost/admin/), the API at [localhost/api/](localhost/api/) and the API docs at [localhost/api/docs/](localhost/api/docs/).

### API Usage Example

#### Query

```http
GET localhost/api/recipes/
```

#### Response
```json
{
  "count": 123,
  "next": "http://localhost/api/recipes/?page=4",
  "previous": "http://localhost/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://localhost/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

## Used Tech

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)

![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)

![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

## Author

Created by Dmitry Fofanov