# PPE Architecture

Pipeline:

IN → SIG → PAT → DEC → OUT

## Layers

1. Input Layer
2. Signature Layer (hash + identity)
3. Pattern Engine
4. Decision Engine
5. Proof Engine (RSA / hash binding)

---

## Output

Proof = {
  proof_id,
  input_hash,
  final_hash,
  signature
}