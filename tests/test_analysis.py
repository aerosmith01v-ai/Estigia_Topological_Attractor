import unittest

from analysis import analyze, analyze_sofi


class AnalysisTests(unittest.TestCase):
    def test_series_stats_and_slope(self):
        result = analyze({"serie": [1, 3, 5], "horizonte": 2})
        self.assertEqual(result["estadisticas"]["tendencia_por_muestra"], 2.0)
        self.assertEqual(result["extrapolacion_lineal"]["valor_estimado"], 9.0)

    def test_pair_gap_forward_and_reverse(self):
        result = analyze({"serie": [1, 2], "entrada": 4, "salida": 7})
        pair = result["comparacion_entrada_salida"]
        self.assertEqual(pair["brecha_salida_menos_entrada"], 3)
        self.assertEqual(pair["diferencia_inversa_entrada_menos_salida"], -3)

    def test_threshold_crossing_estimate(self):
        result = analyze({"serie": [1, 2, 3], "umbral": 5, "horizonte": 3})
        self.assertEqual(result["umbral"]["estimacion_lineal_supera_umbral_en_muestras"], 2.0)
        self.assertTrue(result["umbral"]["extrapolacion_lineal_cruza_umbral"])

    def test_sofi_formula_output_is_labeled_heuristic(self):
        result = analyze_sofi({"frecuenciaActual": 12.3, "ritmoCardiaco": 72})
        self.assertEqual(result["entrada"]["banda"], "Alpha")
        self.assertIn("heurísticas", result["limites"])

    def test_bad_series_rejected(self):
        with self.assertRaises(ValueError):
            analyze({"serie": [1]})

    def test_zero_entry_relative_gap_is_undefined(self):
        result = analyze({"serie": [1, 2], "entrada": 0, "salida": 2})
        self.assertIsNone(result["comparacion_entrada_salida"]["brecha_relativa_sobre_entrada"])


if __name__ == "__main__":
    unittest.main()
