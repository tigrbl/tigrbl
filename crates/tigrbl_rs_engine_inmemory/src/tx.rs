use std::{
    collections::BTreeMap,
    sync::{Arc, Mutex},
};

use tigrbl_rs_ports::{
    errors::{PortError, PortResult},
    transactions::TransactionPort,
};
use tigrbl_rs_spec::{request::RequestEnvelope, response::ResponseEnvelope, values::Value};

pub(crate) type Row = BTreeMap<String, Value>;
pub(crate) type TableRows = Vec<Row>;
pub(crate) type Store = BTreeMap<String, TableRows>;

#[derive(Debug)]
pub struct InmemoryTransaction {
    shared: Arc<Mutex<Store>>,
    working: Mutex<Store>,
}

impl InmemoryTransaction {
    pub fn new(shared: Arc<Mutex<Store>>) -> Self {
        let snapshot = shared
            .lock()
            .expect("inmemory store mutex poisoned")
            .clone();
        Self {
            shared,
            working: Mutex::new(snapshot),
        }
    }
}

impl TransactionPort for InmemoryTransaction {
    fn commit(&self) -> PortResult<()> {
        let working = self
            .working
            .lock()
            .map_err(|_| PortError::Message("transaction state poisoned".to_string()))?
            .clone();
        let mut shared = self
            .shared
            .lock()
            .map_err(|_| PortError::Message("shared store poisoned".to_string()))?;
        *shared = working;
        Ok(())
    }

    fn rollback(&self) -> PortResult<()> {
        Ok(())
    }

    fn execute(
        &self,
        table: &str,
        _operation: &str,
        kind: &str,
        request: &RequestEnvelope,
    ) -> PortResult<ResponseEnvelope> {
        let mut working = self
            .working
            .lock()
            .map_err(|_| PortError::Message("transaction state poisoned".to_string()))?;
        let rows = working.entry(table.to_string()).or_default();

        match kind {
            "create" => {
                let row = body_object(&request.body)?;
                rows.push(row.clone());
                Ok(ResponseEnvelope {
                    status: 201,
                    headers: BTreeMap::new(),
                    body: Value::Object(row),
                })
            }
            "read" => {
                let row = find_row(rows, request)
                    .cloned()
                    .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(row),
                })
            }
            "update" | "replace" => {
                let body = body_object(&request.body)?;
                let row = find_row_mut(rows, request)
                    .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                *row = body.clone();
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(body),
                })
            }
            "merge" => {
                let body = body_object(&request.body)?;
                let row = find_row_mut(rows, request)
                    .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                for (key, value) in body {
                    row.insert(key, value);
                }
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(row.clone()),
                })
            }
            "delete" => {
                let id = find_id(request)
                    .ok_or_else(|| PortError::Message("missing id for delete".to_string()))?;
                let position = rows
                    .iter()
                    .position(|row| row.get("id") == Some(&id))
                    .ok_or_else(|| PortError::Message(format!("row not found in {table}")))?;
                let removed = rows.remove(position);
                Ok(ResponseEnvelope {
                    status: 200,
                    headers: BTreeMap::new(),
                    body: Value::Object(removed),
                })
            }
            "list" => Ok(ResponseEnvelope {
                status: 200,
                headers: BTreeMap::new(),
                body: Value::Array(rows.iter().cloned().map(Value::Object).collect()),
            }),
            _ => Err(PortError::not_implemented(kind)),
        }
    }
}

fn body_object(body: &Value) -> PortResult<Row> {
    match body {
        Value::Object(value) => Ok(value.clone()),
        _ => Err(PortError::Message(
            "request body must be an object for write operations".to_string(),
        )),
    }
}

fn find_id(request: &RequestEnvelope) -> Option<Value> {
    request
        .path_params
        .get("id")
        .cloned()
        .or_else(|| request.query_params.get("id").cloned())
        .or_else(|| match &request.body {
            Value::Object(object) => object.get("id").cloned(),
            _ => None,
        })
}

fn find_row<'a>(rows: &'a [Row], request: &RequestEnvelope) -> Option<&'a Row> {
    let id = find_id(request)?;
    rows.iter().find(|row| row.get("id") == Some(&id))
}

fn find_row_mut<'a>(rows: &'a mut [Row], request: &RequestEnvelope) -> Option<&'a mut Row> {
    let id = find_id(request)?;
    rows.iter_mut().find(|row| row.get("id") == Some(&id))
}
