# Daily Guess

## References

- [Loldle](https://loldle.net/classic)
- [Dotadle](https://dotadle.net/)
- [Wordle](https://www.nytimes.com/games/wordle/index.html)

## Key features

### Game Guess

A new game for a guess is selected every day.
The game will consist of 3 parts:
- Guess by attributes (genre, year, ...)
- Guess by screenshot
- Guess by game character

Only 1 correct guess per day is allowed to users.We will be tracking their guesses and display the global score.

This feature also aims to engage users and obtain more traffic and sign ups.

### Guess by attributes

- Genre
- Free to play
- Singleplayer / Multiplayer
- Release Year
- Disk Storage
- RAM Memory

### Guess by screenshot

A set of screenshots is provided. One screenshot is randomly selected and displayed to users.
After guessing, a difference of attributes is displayed to users to show them in which direction to move.

### Guess by game character

A set of characters is provided. One picture is randomly selected and displayed to users.
After guessing, a difference of attributes is displayed to users to show them in which direction to move.

## Implementation

### Schema

**Guess Game**

This object defines a single guess game that will be picked for a guess

```json
{
    "_id": "1234567890",
    // game that should be guessed
    "product_id": "1",
    // guess type, one of: "attributes", "screenshot", "character"
    "type": "attributes",
    // game data, dynamic, depends on type
    "data": {},

    "created_at": "2024-02-03T00:00:00Z",
    "updated_at": "2024-02-03T00:00:00Z"
}
```

**Daily Guess Game**

This object defines which guess game should be displayed on which day.

```json
{
    "_id": "123456",
    // optional, guess game data parent, if not provided - custom game
    "guess_game_id": "1234567890",
    // game that should be guessed
    "product_id": "1",
    // guess type, one of: "attributes", "screenshot", "character"
    "type": "attributes",
    // game data
    "data": {},
    // when to display
    "display_at": "2024-09-09T00:00:00Z",

    "created_at": "2024-02-03T00:00:00Z",
    "updated_at": "2024-02-03T00:00:00Z"
}
```

**Game Guess**

This object describes a set of guesses (correct or incorrect) per 1 user (either signed in or signed out).

```json
{
    "_id": "456",
    // A daily guessed game
    "daily_guess_game_id": "123456",
    // ip address of the one who guessed
    "ip": "127.0.0.1",
    // optional field, only present when signed in, points to the one who guessed
    "profile_id": "2",
    // attempts a user made to guess
    "attempts": [{ "product_id": "1234", "data": {} }],
    // when a user guessed - date or null, where null means a user is still guessing
    // note: (guessed_at - created_at) is the total time a user spent to guess the game 
    "guessed_at": null,

    "created_at": "2024-02-03T00:00:00Z",
    "updated_at": "2024-02-03T00:00:00Z"
}
```

### Concept

The idea is to create a template `Guess game` that will be user for regular generation of a `Daily guess game`. Users then will be tracked as `Game guess`.

Guess game has an attribute `data` that defines what can be used for a guess. Example:

```json
{
    "data": {
        "screenshots": ["http://...", "http://..."]
    }
}
```

One of the above screenshots will be randomly picked later for a daily guess.

Data is either copied from the original `product` or defined by an Admin.
For games with type `attributes`, we would not normally define anything, unless we want to override something that should be copied from the original product without changing the product itself.

### Admin Panel

We need a bunch of endpoints to manage daily games.

#### Guess games

**POST /v1/admin/guess_games**

Create a guess game

```json
{
    // a game to guess
    "product_id": "123456",
    // one of: "attributes", "screenshot", "character"
    "type": "attributes",
    // dynamic object, depends on type
    "data": {
        "key1": "val1",
        "key2": "val2"
    }
}
```

**GET /v1/admin/guess_games**

List all guess games

**GET /v1/admin/guess_games/:id**

Get a guess game by id

**DELETE /v1/admin/guess_games/:id**

Delete a guess game by id

**PATCH /v1/admin/guess_games/:id**

Patch a guess game by id

```json
{
    // optional
    "product_id": "123456",
    // optional, one of: "attributes", "screenshot", "character"
    "type": "attributes",
    // optional
    "data": {
        "key1": "val1",
        "key2": "val2"
    }
}
```

#### Daily guess games

**POST /v1/admin/daily_guess_games**

Create a custom daily guess game

```json
{
    // game that should be guessed
    "product_id": "1",
    // guess type, one of: "attributes", "screenshot", "character"
    "type": "attributes",
    // game data
    "data": {},
    // when to display
    "display_at": "2024-09-09T00:00:00Z",
}
```

**GET /v1/admin/daily_guess_games**

List all daily guess games

**GET /v1/admin/daily_guess_games/:id**

Get a daily guess game by id

**DELETE /v1/admin/daily_guess_games/:id**

Delete a daily guess game by id

**PATCH /v1/admin/daily_guess_games/:id**

Patch a daily guess game by id

```json
{
    // optional
    "product_id": "123456",
    // optional, one of: "attributes", "screenshot", "character"
    "type": "attributes",
    // optional
    "data": {
        "key1": "val1",
        "key2": "val2"
    },
    // optional
    "display_at": "2024-06-03T00:00:00Z",
}
```

### Protected with service account token access

**GET /v1/guess_games/today**

Get a daily guess game for today. Should be called from NextJS server.
Returns a daily guess game matched by FLOOR(`display_at`) == TODAY.

**POST /v1/guess_games/tomorrow**

Generate a daily guess game for the next day. Will be called from a daily cron job.

### Public

**POST /v1/guess_games/:id/guesses**

Track user guesses.

```json
{
    "product_id": "1234567"
}
```

The first call to the endpoint will create an object in DB with 1 attempt. All subsequent calls will update its attempts.

The guess validation should happen on backend.
Independently of the result we should track a user guess.
If a user guesses, we should track the `guessed_at` timestamp.

Validations:
- Do not allow users that have already guessed correctly to guess again (match by IP)
- Backend must validate if the answer provided by user matches the expected result

For all of the game types, in `attempts.data` we should store the difference of attributes to show users what they guessed and what they didn't, so that they know in which direction to move.

If the auth token is present, also track the `profile_id`

### Protected with user token

**GET /v1/me/game_guesses**

List all guesses by profile id

**PATCH /v1/game_guesses/:id**

Link a game guess to a profile. Find a game guess by id AND ip address and update its profile id.

Example:

```python
collection.find_one_and_update(
    { "_id": game_guess_id, "ip": request.ip, "profile_id": null },
    { "profile_id": request.auth.id }
)
```

If a guess is not found, return 404 error.