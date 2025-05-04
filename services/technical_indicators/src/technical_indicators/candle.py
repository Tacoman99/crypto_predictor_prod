from config import config
from quixstreams import State


def same_window(candle1: dict, candle2: dict) -> bool:
    """
    Check if two candles are in the same window
    """
    return (
        candle1['pair'] == candle2['pair']
        and candle1['window_start_ms'] == candle2['window_start_ms']
        and candle1['window_end_ms'] == candle2['window_end_ms']
    )


def update_candles_state(candle: dict, state: State):
    """
    Update the state with the new candle
    """
    # Get the current count from the state
    candles = state.get('candles', default=[])

    # Need to check if the new candle corresponds to
    if not candles:
        candles.append(candle)
    elif same_window(candle, candles[-1]):
        candles[-1] = candle
    else:
        # add new candle to the list
        candles.append(candle)

    if len(candles) > config.max_candles_in_state:
        # remove the oldest candle
        candles.pop(0)

    # update the state with candles
    state.set('candles', candles)

    return candle
