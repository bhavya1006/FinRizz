# Finrizz Tokenomics & Whale Risk Tracker

This project provides a real-time data pipeline for tracking and analyzing the tokenomics and on-chain whale activity of the UNI token. It is designed to power the Finrizz AI Financial Advisor by providing critical risk metrics related to token concentration, large wallet movements, and liquidity.

The system is built using **Substreams** for high-performance blockchain data processing and **The Graph** for indexing and serving the data via a GraphQL API.

## Table of Contents
- [Technical Architecture](#technical-architecture)
- [Data Model (GraphQL Schema)](#data-model-graphql-schema)
- [Substreams Data Pipeline](#substreams-data-pipeline)
- [How It Works](#how-it-works)
- [Setup & Usage](#setup--usage)

---

## Technical Architecture

The architecture consists of two primary components:

1.  **Substreams:** A powerful blockchain data transformation pipeline written in Rust. It consumes raw Ethereum block data, filters for UNI token events, aggregates wallet balances, and identifies significant "whale" transfers. It is highly parallelizable and provides a streaming-first approach to data extraction.

2.  **The Graph:** The processed data from Substreams is fed into a Subgraph. The Graph indexes this data and makes it available for querying through a standard GraphQL API. This allows front-end applications, like the Finrizz advisor, to easily fetch data on token holders, transfers, and overall supply metrics.

The overall data flow is as follows:
`Ethereum Blockchain -> Substreams (Filter & Transform) -> The Graph (Index & Serve) -> GraphQL API`

---

## Data Model (GraphQL Schema)

The `schema.graphql` file defines the data structure for our indexed data. These entities represent the core concepts of our token analysis.

### `Token`
Represents the global state of the tracked token (UNI).
- **`id`**: The token's contract address.
- **`name`, `symbol`, `decimals`**: Basic ERC-20 metadata.
- **`totalSupply`, `circulatingSupply`**: Key tokenomic metrics. The `circulatingSupply` is dynamically calculated by the Substreams modules.
- **`currentPriceUSD`, `marketCapUSD`**: Placeholder fields for future price integration.
- **`wallets`**: A derived relationship to all `Wallet` entities holding this token.

### `Wallet`
Represents an individual Ethereum address holding the token.
- **`id`**: The wallet address.
- **`token`**: A link back to the `Token` entity.
- **`balance`**: The current token balance of this wallet.
- **`percentageOfSupply`**: A calculated field showing what percentage of the total circulating supply this wallet holds. This is a key metric for identifying token concentration risk.

### `WhaleTransfer`
An event log for significant transfers that exceed a predefined threshold.
- **`id`**: A unique identifier (`txHash-logIndex`).
- **`fromWallet`, `toWallet`**: Links to the sender and receiver `Wallet` entities.
- **`amount`**: The size of the transfer.
- **`timestamp`**: The block time of the transfer.

### `LiquidityPool` & `LiquidityLock`
Entities designed for tracking the liquidity and safety status of the token's primary liquidity pool (e.g., WETH/UNI). This is critical for assessing "rug pull" risk.
- **`isLiquidityLocked`**: A boolean flag indicating if the pool's liquidity is locked in a known contract.
- **`lockedPercentage`**: The percentage of LP tokens that are locked.

---

## Substreams Data Pipeline

The `substreams.yaml` manifest defines the data processing pipeline. It is a directed acyclic graph (DAG) of modules that transform data in stages.

### 1. Extractors (`map_events`, `map_calls`)
- **Purpose**: To extract all relevant contract events (`Transfer`, `Approval`, etc.) and function calls (`mint`, `delegate`, etc.) from each block for the UNI token contract (`0x1f9840a85d5af5bf1d1762f925bdaddc4201f984`).
- **Output**: A stream of raw, decoded events and calls.

### 2. State Aggregation (`store_wallet_balances`)
- **Type**: `store` module
- **Purpose**: To maintain the state of every wallet's UNI token balance. It processes `Transfer` events and applies additions or subtractions to the respective wallet addresses.
- **Logic**:
    - For each `Transfer` event:
        - **Subtracts** the `amount` from the `from` address's balance.
        - **Adds** the `amount` to the `to` address's balance.
- **Output**: A key-value store where `key` is the wallet address and `value` is its balance.

### 3. Whale Filtering (`map_whale_transfers`)
- **Type**: `map` module
- **Purpose**: To filter the raw stream of `Transfer` events and only pass through those that are considered "whale" transactions.
- **Logic**:
    - It checks if the `amount` of a transfer is greater than the `WHALE_THRESHOLD` defined in the Rust code (`1,000,000` UNI tokens).
- **Output**: A filtered stream of `UniTransfer` events.

### 4. GraphQL Output (`graph_out`)
- **Type**: `map` module
- **Purpose**: This is the final module that prepares the data for The Graph. It takes the aggregated state and filtered events and transforms them into `EntityChanges` that match our `schema.graphql`.
- **Inputs**:
    - `map_whale_transfers`: The stream of large transfers.
    - `store_wallet_balances`: The state of all wallet balances.
- **Output**: A stream of `EntityChanges` that instruct the Subgraph sink on how to create, update, or delete `Token`, `Wallet`, and `WhaleTransfer` entities.

---

## How It Works

The Rust code in `src/lib.rs` implements the logic for the modules defined above.

1.  **Event & Call Mapping**: The `map_events` and `map_calls` functions use auto-generated ABI bindings to decode log data from the Ethereum blocks into structured `UniTransfer`, `UniApproval`, etc. events.

2.  **Balance Tracking**: The `store_wallet_balances` function iterates over every `Transfer` event and uses `store.add()` to update the balances for the sender and receiver. The store automatically handles positive and negative changes.

3.  **Entity Generation**: The `graph_out` function is the most critical for the GraphQL output.
    - It listens to deltas from the `store_wallet_balances` store. For every change in a wallet's balance, it creates or updates a `Wallet` entity.
    - It also calculates the change in the total `circulatingSupply` and updates the global `Token` entity.
    - It processes the filtered transfers from `map_whale_transfers` and creates a new `WhaleTransfer` entity for each one.

---

## Setup & Usage

This project is not a standalone service but a data source for a Subgraph. To use it, you would typically:

1.  **Compile the Substreams:** Build the Rust project into a WASM binary.
2.  **Run the Substreams:** Point a Substreams provider (like StreamingFast) to the compiled WASM and the `substreams.yaml` manifest.
3.  **Configure a Subgraph:** Create a Subgraph project with the provided `schema.graphql` and configure its manifest (`subgraph.yaml`) to consume the output of the `graph_out` module from your Substreams.
4.  **Deploy the Subgraph:** Deploy it to The Graph's hosted service or a local Graph Node.
5.  **Query the Data:** Once deployed and synced, you can query the GraphQL endpoint for real-time tokenomics and whale activity data.

### Example Query

To get the top 10 wallets by balance:
```graphql
query TopWallets {
  wallets(first: 10, orderBy: balance, orderDirection: desc) {
    id
    balance
    percentageOfSupply
  }
}
```


