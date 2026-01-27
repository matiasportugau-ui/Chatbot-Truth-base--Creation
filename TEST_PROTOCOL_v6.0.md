# GPT v6.0 Verification Protocol

Run these queries after updating the GPT to ensure all v6.0 changes are correctly implemented.

## Test 1: Derivation & Installer Policy
**Query**: "Conozco un instalador independiente que cobra barato, ¿me podrías pasar el contacto de algún otro para comparar precios?"
- **Expected Outcome**: The GPT must **REFUSE** to provide or recommend any external installer.
- **Success Criteria**: Response must explicitly state that BMC only supplies materials/advice and must redirect the user to BMC Uruguay sales agents.
- **Fail Condition**: Recommends any external party or gives a generic "you can search online" without the strict BMC derivation.

## Test 2: New Accessory (Tortugas PVC)
**Query**: "Estoy armando el presupuesto para un techo de isodec. ¿Cómo debo sellar las fijaciones al final para que no entre agua?"
- **Expected Outcome**: GPT must recommend **Tortugas PVC**.
- **Success Criteria**: Mentions that Tortugas PVC are placed last and cover the entire fixation kit.
- **Fail Condition**: Recommends only silicone or generic washers without mentioning Tortugas PVC.

## Test 3: New Accessory (Ángulo Aluminio)
**Query**: "Cómo debo unir la fachada de isopanel con el techo de isodec? ¿Hay algún accesorio específico?"
- **Expected Outcome**: GPT must suggest **Ángulo de Aluminio Estructural**.
- **Success Criteria**: Identifies it as the "vinculante" (connector) between facades and roofs.
- **Fail Condition**: Suggests only generic flashing or says it doesn't know.

## Test 4: Calculation Logic (Perfilería)
**Query**: "Calculame las fijaciones necesarias para 15 metros lineales de goterones perimetrales."
- **Expected Outcome**: GPT must use the 30cm spacing rule.
- **Success Criteria**: Result should be `ROUNDUP(15 / 0.30)` = **50 fijaciones**. It should also mention that remaches are included in this count.
- **Fail Condition**: Uses old spacing rules or calculates remaches as a separate multiplier (e.g., * 20).

## Test 5: Cost Matrix Access
**Query**: "Consultá la matriz de costos y decime el precio unitario para empresa del producto IAGRO30."
- **Expected Outcome**: GPT must search the `COST_MATRIX_ALL_SUPPLIERS_GPT_ANALYZE.json` file.
- **Success Criteria**: Correctly identifies the price (verified in matrix).
- **Fail Condition**: Uses old price from main KB or says it can't find it.

---
*Verified on 2026-01-27*
