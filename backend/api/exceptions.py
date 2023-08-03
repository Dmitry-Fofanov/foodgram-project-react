from rest_framework.exceptions import APIException


class AlreadyFavoriteException(APIException):
    status_code = 400
    default_code = 'already_favorite'
    default_detail = 'Recipe already is in favorites.'


class NotFavoriteException(APIException):
    status_code = 400
    default_code = 'not_favorite'
    default_detail = 'Recipe is not in favorites.'


class AlreadyInShoppingCart(APIException):
    status_code = 400
    default_code = 'already_in_cart'
    default_detail = 'Recipe already is in the shopping cart.'


class NotInCartException(APIException):
    status_code = 400
    default_code = 'not_in_cart'
    default_detail = 'Recipe is not in the shopping cart.'


class AlreadyFollowingException(APIException):
    status_code = 400
    default_code = 'already_following'
    default_detail = 'Already following the user.'


class NotFollowingException(APIException):
    status_code = 400
    default_code = 'not_following'
    default_detail = 'Not following the user.'
