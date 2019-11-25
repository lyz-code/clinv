# Migration notes

## 0.5.1 -> 0.6.0

* Services without aws resources must have the `aws: {}` value in the user_data
  yaml. `aws: null` will fail.
