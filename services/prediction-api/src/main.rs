use axum::{
    routing::get,
    extract::Query,
    // http::StatusCode,
    // Json,
    Router,
};
use serde::Deserialize;
use sqlx::postgres::PgPoolOptions;

// This is how you denote the entrypoint of a Rust program that uses async with tokio
#[tokio::main]
async fn main() {
    
    // build our application with a route
    let app = Router::new()
        // `GET /` goes to `root`
        .route("/health", get(health))
        .route("/predictions", get(get_prediction));

    // run our app with hyper, listening globally on port 3000
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3009").await.unwrap();
    
    axum::serve(listener, app).await.unwrap();
}

// basic handler that responds with a static string
async fn health() -> &'static str {
    // let name: String = "my name".to_string();

    "I am healthy!"
}

#[derive(Deserialize)]
struct PredictionParams {
    pair: String,
}

async fn get_prediction(params: Query<PredictionParams>) -> String {
    
    // TODO: debug why we are getting nulls here. This is what generates an invalid sql query that returns no data.
    let pair = &params.0.pair;

    // Return a message that depends on the pair
    // In python you would write something like this
    // output = f'You want predictons for {pair}'

    // Create a connection pool so we can talk to RisingWave (which under the hood is
    // a postgres + other things)
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://root:123@localhost:4567/dev").await.unwrap();

    // Make a simple query to return the given parameter (use a question mark `?` instead of `$1` for MySQL/MariaDB)
    // let row: (i64,) = sqlx::query_as("SELECT $1")
    //     .bind(150_i64)
    //     .fetch_one(&pool).await.unwrap();
    // assert_eq!(row.0, 150);

    #[derive(sqlx::FromRow)]
    struct PredictionOutput { pair: String, predicted_price: f64 }

    // TODO: use the actual value from `pair` and string formatting to generate the correct sql query
    // Modify the query so that we get the latest `predicted_price` for the given `pair`
    // let query = "SELECT pair, predicted_price FROM public.predictions WHERE pair = 'BTC/USD'";
    let query = format!("SELECT pair, predicted_price FROM public.predictions WHERE pair = '{}'", pair);

    let prediction_output = sqlx::query_as::<_, PredictionOutput>(
        &query
    )
    // .bind(pair)
    .fetch_one(&pool).await.unwrap();

    let output = format!(
        "The price prediction for {} is {}",
        prediction_output.pair, prediction_output.predicted_price);

    // TODO: return a formatted JSON with the predicted_price, not a string like this.
    return output

}
