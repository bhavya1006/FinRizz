mod abi;
mod pb;
use hex_literal::hex;
use pb::contract::v1 as contract;
use substreams::Hex;
use substreams_ethereum::pb::eth::v2 as eth;
use substreams_ethereum::Event;

// === [ A D D I T I O N S ] ===
use substreams::store::{StoreAdd, StoreAddBigInt, StoreGet, StoreGetBigInt, StoreNew, StoreSet, StoreSetRaw};
use substreams::store::pb::bigint::BigInt as StoreBigInt; // Alias for the store BigInt


// Crate used for creating the GraphQL entities
#[allow(unused_imports)]
use num_traits::cast::ToPrimitive;
use std::str::FromStr;
use substreams::scalar::BigDecimal;
use substreams_entity_change::pb::entity::EntityChanges;
use num_bigint::{BigInt, Sign};
use lazy_static::lazy_static;

substreams_ethereum::init!();

const UNI_TRACKED_CONTRACT: [u8; 20] = hex!("1f9840a85d5af5bf1d1762f925bdaddc4201f984");

lazy_static! {
    static ref WHALE_THRESHOLD: num_bigint::BigInt = {
	"10000000000000000000000".parse().unwrap()
	};
}
fn map_uni_events(blk: &eth::Block, events: &mut contract::Events) {
    events.uni_approvals.append(&mut blk
        .receipts()
        .flat_map(|view| {
            view.receipt.logs.iter()
                .filter(|log| log.address == UNI_TRACKED_CONTRACT)
                .filter_map(|log| {
                    if let Some(event) = abi::uni_contract::events::Approval::match_and_decode(log) {
                        return Some(contract::UniApproval {
                            evt_tx_hash: Hex(&view.transaction.hash).to_string(),
                            evt_index: log.block_index,
                            evt_block_time: Some(blk.timestamp().to_owned()),
                            evt_block_number: blk.number,
                            amount: event.amount.to_string(),
                            owner: event.owner,
                            spender: event.spender,
                        });
                    }

                    None
                })
        })
        .collect());
    events.uni_delegate_changeds.append(&mut blk
        .receipts()
        .flat_map(|view| {
            view.receipt.logs.iter()
                .filter(|log| log.address == UNI_TRACKED_CONTRACT)
                .filter_map(|log| {
                    if let Some(event) = abi::uni_contract::events::DelegateChanged::match_and_decode(log) {
                        return Some(contract::UniDelegateChanged {
                            evt_tx_hash: Hex(&view.transaction.hash).to_string(),
                            evt_index: log.block_index,
                            evt_block_time: Some(blk.timestamp().to_owned()),
                            evt_block_number: blk.number,
                            delegator: event.delegator,
                            from_delegate: event.from_delegate,
                            to_delegate: event.to_delegate,
                        });
                    }

                    None
                })
        })
        .collect());
    events.uni_delegate_votes_changeds.append(&mut blk
        .receipts()
        .flat_map(|view| {
            view.receipt.logs.iter()
                .filter(|log| log.address == UNI_TRACKED_CONTRACT)
                .filter_map(|log| {
                    if let Some(event) = abi::uni_contract::events::DelegateVotesChanged::match_and_decode(log) {
                        return Some(contract::UniDelegateVotesChanged {
                            evt_tx_hash: Hex(&view.transaction.hash).to_string(),
                            evt_index: log.block_index,
                            evt_block_time: Some(blk.timestamp().to_owned()),
                            evt_block_number: blk.number,
                            delegate: event.delegate,
                            new_balance: event.new_balance.to_string(),
                            previous_balance: event.previous_balance.to_string(),
                        });
                    }

                    None
                })
        })
        .collect());
    events.uni_minter_changeds.append(&mut blk
        .receipts()
        .flat_map(|view| {
            view.receipt.logs.iter()
                .filter(|log| log.address == UNI_TRACKED_CONTRACT)
                .filter_map(|log| {
                    if let Some(event) = abi::uni_contract::events::MinterChanged::match_and_decode(log) {
                        return Some(contract::UniMinterChanged {
                            evt_tx_hash: Hex(&view.transaction.hash).to_string(),
                            evt_index: log.block_index,
                            evt_block_time: Some(blk.timestamp().to_owned()),
                            evt_block_number: blk.number,
                            minter: event.minter,
                            new_minter: event.new_minter,
                        });
                    }

                    None
                })
        })
        .collect());
    events.uni_transfers.append(&mut blk
        .receipts()
        .flat_map(|view| {
            view.receipt.logs.iter()
                .filter(|log| log.address == UNI_TRACKED_CONTRACT)
                .filter_map(|log| {
                    if let Some(event) = abi::uni_contract::events::Transfer::match_and_decode(log) {
			
			// **1. Get amount as Rust BigInt for comparison**
			//let amount_str = event.amount.to_string();
			//let amount_bigint = BigInt::from_str(&amount_str).unwrap_or_default();

			return Some(contract::UniTransfer {
                           	evt_tx_hash: Hex(&view.transaction.hash).to_string(),
                            	evt_index: log.block_index,
                            	evt_block_time: Some(blk.timestamp().to_owned()),
                            	evt_block_number: blk.number,
                            	amount: event.amount.to_string(),
                            	from: event.from,
                            	to: event.to,
                        	});
                        }
                    None
                })
        })
        .collect());
}
fn map_uni_calls(blk: &eth::Block, calls: &mut contract::Calls) {
    calls.uni_call_approves.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::Approve::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::Approve::decode(call) {
                        Ok(decoded_call) => {
                            let output_param0 = match abi::uni_contract::functions::Approve::output(&call.return_data) {
                                Ok(output_param0) => {output_param0}
                                Err(_) => Default::default(),
                            };
                            
                            Some(contract::UniApproveCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                output_param0: output_param0,
                                raw_amount: decoded_call.raw_amount.to_string(),
                                spender: decoded_call.spender,
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
    calls.uni_call_delegates.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::Delegate::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::Delegate::decode(call) {
                        Ok(decoded_call) => {
                            Some(contract::UniDelegateCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                delegatee: decoded_call.delegatee,
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
    calls.uni_call_delegate_by_sigs.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::DelegateBySig::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::DelegateBySig::decode(call) {
                        Ok(decoded_call) => {
                            Some(contract::UniDelegateBySigCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                delegatee: decoded_call.delegatee,
                                expiry: decoded_call.expiry.to_string(),
                                nonce: decoded_call.nonce.to_string(),
                                r: Vec::from(decoded_call.r),
                                s: Vec::from(decoded_call.s),
                                v: decoded_call.v.to_u64(),
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
    calls.uni_call_mints.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::Mint::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::Mint::decode(call) {
                        Ok(decoded_call) => {
                            Some(contract::UniMintCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                dst: decoded_call.dst,
                                raw_amount: decoded_call.raw_amount.to_string(),
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
    calls.uni_call_permits.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::Permit::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::Permit::decode(call) {
                        Ok(decoded_call) => {
                            Some(contract::UniPermitCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                deadline: decoded_call.deadline.to_string(),
                                owner: decoded_call.owner,
                                r: Vec::from(decoded_call.r),
                                raw_amount: decoded_call.raw_amount.to_string(),
                                s: Vec::from(decoded_call.s),
                                spender: decoded_call.spender,
                                v: decoded_call.v.to_u64(),
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
    calls.uni_call_set_minters.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::SetMinter::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::SetMinter::decode(call) {
                        Ok(decoded_call) => {
                            Some(contract::UniSetMinterCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                minter: decoded_call.minter,
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
    calls.uni_call_transfers.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::Transfer::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::Transfer::decode(call) {
                        Ok(decoded_call) => {
                            let output_param0 = match abi::uni_contract::functions::Transfer::output(&call.return_data) {
                                Ok(output_param0) => {output_param0}
                                Err(_) => Default::default(),
                            };
                            
                            Some(contract::UniTransferCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                dst: decoded_call.dst,
                                output_param0: output_param0,
                                raw_amount: decoded_call.raw_amount.to_string(),
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
    calls.uni_call_transfer_froms.append(&mut blk
        .transactions()
        .flat_map(|tx| {
            tx.calls.iter()
                .filter(|call| call.address == UNI_TRACKED_CONTRACT && abi::uni_contract::functions::TransferFrom::match_call(call))
                .filter_map(|call| {
                    match abi::uni_contract::functions::TransferFrom::decode(call) {
                        Ok(decoded_call) => {
                            let output_param0 = match abi::uni_contract::functions::TransferFrom::output(&call.return_data) {
                                Ok(output_param0) => {output_param0}
                                Err(_) => Default::default(),
                            };
                            
                            Some(contract::UniTransferFromCall {
                                call_tx_hash: Hex(&tx.hash).to_string(),
                                call_block_time: Some(blk.timestamp().to_owned()),
                                call_block_number: blk.number,
                                call_ordinal: call.begin_ordinal,
                                call_success: !call.state_reverted,
                                dst: decoded_call.dst,
                                output_param0: output_param0,
                                raw_amount: decoded_call.raw_amount.to_string(),
                                src: decoded_call.src,
                            })
                        },
                        Err(_) => None,
                    }
                })
        })
        .collect());
}

#[substreams::handlers::map]
fn map_events_calls(
    events: contract::Events,
    calls: contract::Calls,
) -> Result<contract::EventsCalls, substreams::errors::Error> {
    Ok(contract::EventsCalls {
        events: Some(events),
        calls: Some(calls),
    })
}
#[substreams::handlers::map]
fn map_events(blk: eth::Block) -> Result<contract::Events, substreams::errors::Error> {
    let mut events = contract::Events::default();
    map_uni_events(&blk, &mut events);
    Ok(events)
}
#[substreams::handlers::map]
fn map_calls(blk: eth::Block) -> Result<contract::Calls, substreams::errors::Error> {
let mut calls = contract::Calls::default();
    map_uni_calls(&blk, &mut calls);
    Ok(calls)
}


// --- 💰 STORE MODULE: Wallet Balances (Stateful) ---
#[substreams::handlers::store]
fn store_wallet_balances(
    // Input: The raw transfers (unfiltered) or the result of map_events
    events: contract::Events, 
    store: substreams::store::StoreAddBigInt
) {
    for transfer in events.uni_transfers {
        let amount = StoreBigInt::from_str(&transfer.amount).unwrap_or_default();

        // Sender Balance: Subtract amount
        // Key: Wallet Address (Bytes)
        store.add(&transfer.from.to_hex(), &amount.neg());

        // Receiver Balance: Add amount
        store.add(&transfer.to.to_hex(), &amount);
    }
}




#[substreams::handlers::map]
fn graph_out(
    // Input 1: Filtered whale transfers (from map_whale_transfers)
    whale_transfers: contract::UniTransfers, 
    // Input 2: Wallet balance deltas (from store_wallet_balances)
    wallet_deltas: substreams::store::Deltas<StoreBigInt> 
) -> Result<EntityChanges, substreams::errors::Error> {
    
    let mut entity_changes: EntityChanges = Default::default();
    
    // The Token ID is constant (the UNI contract address)
    let token_id = Hex(super::UNI_TRACKED_CONTRACT).to_string();

    // ==========================================================
    // 1. WALLET and TOKEN Updates (Concentration & Supply)
    // ==========================================================
    
    for delta in wallet_deltas.deltas {
        let wallet_id = delta.key.clone();
        
        // Use delta.new_value for the current balance
        let balance_str = delta.new_value.to_string();
        
        // Determine if we should CREATE or UPDATE the Wallet entity
        let operation = match delta.operation() {
            // If the key is created or updated, we use Update. The Subgraph sink handles
            // CREATE/UPDATE correctly based on existence.
            substreams::store::DeltaOperation::Update | substreams::store::DeltaOperation::Create => Operation::Update,
            
            // If the balance goes to zero and the key is deleted, you might choose to delete the entity.
            _ => Operation::Update,
        };
        
        // --- A. Update/Create WALLET Entity ---
        entity_changes.push_change(
            "Wallet",
            &wallet_id,
            delta.ordinal(),
            operation,
            &[
                // Set the current balance based on the store output
                ("balance", balance_str.clone()),
                // Link the Wallet to the main Token entity
                ("token", token_id.clone()),
                // NOTE: percentageOfSupply is complex and usually requires the circulatingSupply 
                // value, which should ideally come from a separate store module (omitted for brevity).
            ]
        );
        
        // --- B. Update TOKEN Entity (Circulating Supply) ---
        // Calculate the change in circulating supply using the delta
        // if let Ok(amount) = StoreBigInt::from_str(&delta.old_value.to_string()) {
           //  let circulating_supply_change = StoreBigInt::from_str(&delta.new_value.to_string()).unwrap_or_default() - amount;
	let old_balance = BigInt::from_str(&delta.old_value.to_string()).unwrap_or_default();
	let new_balance = BigInt::from_str(&delta.new_value.to_string()).unwrap_or_default();

	// Calculate the net change: new - old
	let circulating_supply_change = new_balance - old_balance;
	
	if circulating_supply_change.to_string() != "0" {
             // This pushes a change to the TOKEN entity that aggregates the balance changes.
             // Subgraph sink handles this complex aggregation.
             entity_changes.push_change(
                "Token",
                &token_id,
                delta.ordinal(),
                Operation::Update,
                &[
                    // This tells the sink to ADD the change in token balance to the circulatingSupply field.
                    // This is a powerful, non-standard feature of Substreams Entity Changes.
                    ("circulatingSupply", circulating_supply_change.to_string())
                ]
             );
        }
    }

    // ==========================================================
    // 2. CREATE WHALE TRANSFER ENTITIES (Filtered Logs)
    // ==========================================================
    
    for transfer in whale_transfers.uni_transfers {
        // ID: Unique identifier for the transfer event
        let id = format!("{}-{}", transfer.evt_tx_hash, transfer.evt_index);

        entity_changes.push_change(
            "WhaleTransfer", 
            &id, 
            transfer.evt_index,
            Operation::Create,
            &[
                // Link to Token
                ("token", token_id.clone()),
                // Link Wallet entities (address conversion from Bytes to String ID)
                ("fromWallet", Hex::encode(&transfer.from)),
                ("toWallet", Hex::encode(&transfer.to)),
                // Transfer Details
                ("amount", transfer.amount), // The BigInt amount (as string)
                ("timestamp", transfer.evt_block_time.map(|t| t.seconds).unwrap_or_default().to_string()),
                ("txHash", transfer.evt_tx_hash.clone()),
                // ("amountUSD", transfer.amount_usd) // Requires an external price oracle module (complex, often omitted for hackathons)
            ]
        );
    }

    // 3. LIQUIDITY POOL AND LOCKS
    // NOTE: Logic for LiquidityPool and LiquidityLock entities must be added here 
    // after you implement the modules for the Factory/Locker contracts in your substreams.yaml.

    Ok(entity_changes)
}


#[substreams::handlers::map]
fn map_whale_transfers(
    // Input is the output of map_events (containing ALL transfers)
    events: contract::Events
) -> Result<contract::UniTransfers, substreams::errors::Error> {
    
    let mut whale_transfers = contract::UniTransfers::default();

    for transfer in events.uni_transfers {
        // 1. Parse the amount string back into a BigInt for comparison
        let amount_bigint = num_bigint::BigInt::from_str(&transfer.amount).unwrap_or_default();
        
        // 2. APPLY THE WHALE THRESHOLD
        if amount_bigint.ge(&WHALE_THRESHOLD) {
            // Keep the transfer and push it to the output stream
            whale_transfers.uni_transfers.push(transfer);
        }
    }

    Ok(whale_transfers)
}
