# fabrik7

![Version](https://img.shields.io/badge/version-0.1.0-blue)

> Fabrik7 – A simple way to simulate Siemens PLCs

## 🚀 Features
- Simulation of multiple PLCs via built-in Snap7 server
- Configuration support via YAML/JSON file
- Customization of number of PLCs, ports, databases, and data types
- User-friendly CLI interface

## 📦 Installation

### Primary Method
```bash
git clone https://github.com/araujogusta/fabrik7.git
cd fabrik7
pip install .
```

### For development
```bash
git clone https://github.com/araujogusta/fabrik7.git
cd fabrik7

uv sync
uv pip install -e .
```

## 🛠️ How to Use

### Command Structure

```bash
fabrik7 [--log-level <level>] start [--count <n>] [--port <port>] [--db-size <size>] [--db-number <num>] [--dtype <type>] [--config-file <path>]
```

### Practical Examples

```bash
# Example 1: Start 1 default PLC
fabrik7 start

# Example 2: Simulate 5 PLCs, ports starting from 3000, DB of 2048 bytes, 2 DBs per PLC, REAL type
fabrik7 start --count 5 --port 3000 --db-size 2048 --db-number 2 --dtype REAL

# Example 3: Load configurations from a YAML file
fabrik7 start --config-file config.yaml
```

## ⚙️ Commands

| Command   | Options                                                                                                                                                          | Description                                                             |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `fabrik7` | `-l`, `--log-level`                                                                                                                                             | Defines the log level (`DEBUG`, `INFO`, `WARN`, `ERROR`, `CRITICAL`)  |
| `start`   | `-c`, `--count` <n><br>`-p`, `--port` <port><br>`-s`, `--db-size` <size><br>`-n`, `--db-number` <num><br>`-t`, `--dtype` <type><br>`-f`, `--config-file` <path> | Starts servers simulating PLCs with the specified options          |
## 🔧 Configuration

### YAML Configuration Schema

```yaml
plcs:
  - name: PLCName
    port: 2000
    dbs:
      - number: 1
        size: 1024
        fields:
          - name: FieldName
            offset: 0
            dtype: BOOL
            value: true
```

### JSON Configuration Schema

```json
{
    "plcs": [
        {
            "name": "PLC0",
            "port": 2000,
            "dbs": [
                {
                    "number": 1,
                    "size": 1024,
                    "fields": [
                        {
                            "name": "Field0",
                            "offset": 0,
                            "dtype": "BOOL",
                            "value": true
                        }
                    ]
                }
            ]
        }
    ]
}
```

(The fields follow the models defined in `fabrik7.config.models`)
## 🌐 Requirements

* **Python** ≥ 3.13
* **Dependencies**

  * click ≥ 8.2.1
  * pydantic ≥ 2.11.5
  * python-snap7 ≥ 2.0.2
  * pyyaml ≥ 6.0.2

## 🤝 Contributing

Contributions are very welcome!

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Make your commits (`git commit -m 'Add new feature'`)
4. Send to the original branch (`git push origin feature/new-feature`)
5. Open a Pull Request describing your changes
