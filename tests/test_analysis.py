import unittest
from analysis import analyze, analyze_sofi

class AnalysisTests(unittest.TestCase):
    def test_linear_and_reverse_channels_share_data_and_reverse_slope(self):
        result = analyze({"serie": [1, 3, 5], "horizonte": 2})
        self.assertEqual(result["proceso_lineal"]["pendiente_por_muestra"], 2.0)
        self.assertEqual(result["proceso_contraparte"]["pendiente_por_muestra"], -2.0)
        self.assertEqual(result["proceso_lineal"]["extrapolacion_lineal"], 9.0)

    def test_pair_gap_forward_and_reverse(self):
        pair = analyze({"serie": [1, 2], "entrada": 4, "salida": 7})["comparacion_entrada_salida"]
        self.assertEqual(pair["brecha_salida_menos_entrada"], 3)
        self.assertEqual(pair["diferencia_inversa_entrada_menos_salida"], -3)

    def test_text_numbers_and_lexical_summary(self):
        result = analyze({"texto": "lectura 1.5, 2.5, 3.5 patrón patrón"})
        self.assertEqual(result["cantidad_mediciones"], 3)
        self.assertEqual(result["analisis_textual"]["palabras"], 4)

    def test_json_text_series(self):
        result = analyze({"texto": "{\"serie\":[1,2,3]}"})
        self.assertEqual(result["cantidad_mediciones"], 3)

    def test_frequency_features(self):
        result = analyze({"serie": [1, 2, 1, 2, 1, 2]})
        self.assertIsNotNone(result["proceso_lineal"]["frecuencia_dominante"])
        self.assertTrue(result["proceso_lineal"]["autocorrelacion_hasta_100_retardos"])

    def test_sofi_is_labeled_heuristic(self):
        result = analyze_sofi({"frecuenciaActual": 12.3, "ritmoCardiaco": 72})
        self.assertEqual(result["entrada"]["banda"], "Alpha")
        self.assertIn("heurísticas", result["limites"])

    def test_bad_series_rejected(self):
        with self.assertRaises(ValueError):
            analyze({"serie": [1]})

if __name__ == "__main__":
    unittest.main()
