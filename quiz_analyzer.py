#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador do Quiz de Personalidade
Este script analisa o quiz HTML para validar:
1. Distribuição das personalidades nas perguntas
2. Cobertura de todos os 15 perfis
3. Balanceamento das opções
4. Possíveis problemas de pontuação
"""

import re
import json
from collections import Counter, defaultdict
from pathlib import Path

class QuizAnalyzer:
    def __init__(self, quiz_file_path):
        self.quiz_file = Path(quiz_file_path)
        self.questions = []
        self.personalities = set()
        self.personality_distribution = Counter()
        self.question_analysis = []
        
    def load_quiz(self):
        """Carrega e analisa o arquivo HTML do quiz"""
        try:
            with open(self.quiz_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrai as perguntas usando regex
            question_pattern = r'\{\s*id:\s*(\d+),\s*question:\s*"([^"]+)",\s*options:\s*\[(.*?)\]\s*\}'
            option_pattern = r'\{\s*text:\s*"([^"]+)",\s*personality:\s*"([^"]+)"\s*\}'
            
            questions_matches = re.findall(question_pattern, content, re.DOTALL)
            
            for match in questions_matches:
                question_id = int(match[0])
                question_text = match[1]
                options_text = match[2]
                
                # Extrai as opções
                options_matches = re.findall(option_pattern, options_text)
                options = []
                
                for option_match in options_matches:
                    option_text = option_match[0]
                    personality = option_match[1]
                    options.append({
                        'text': option_text,
                        'personality': personality
                    })
                    self.personalities.add(personality)
                    self.personality_distribution[personality] += 1
                
                question_data = {
                    'id': question_id,
                    'question': question_text,
                    'options': options
                }
                
                self.questions.append(question_data)
                
            print(f"✅ Quiz carregado: {len(self.questions)} perguntas encontradas")
            print(f"✅ Personalidades encontradas: {len(self.personalities)}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar quiz: {e}")
            return False
            
        return True
    
    def analyze_personality_distribution(self):
        """Analisa a distribuição das personalidades"""
        print("\n📊 ANÁLISE DA DISTRIBUIÇÃO DAS PERSONALIDADES")
        print("=" * 60)
        
        expected_personalities = {
            "Stratège", "Créatif", "Organisateur", "Communicant", "Leader",
            "Collaboratif", "Mentor", "Indépendant", "Entrepreneur", "Réaliste",
            "Visionnaire", "Méthodique", "Explorateur", "Idéaliste", "Perfectionniste"
        }
        
        # Verifica personalidades ausentes
        missing_personalities = expected_personalities - self.personalities
        extra_personalities = self.personalities - expected_personalities
        
        if missing_personalities:
            print(f"❌ Personalidades ausentes: {missing_personalities}")
        
        if extra_personalities:
            print(f"⚠️  Personalidades extras: {extra_personalities}")
        
        if not missing_personalities and not extra_personalities:
            print("✅ Todas as 15 personalidades estão presentes")
        
        # Analisa distribuição
        print("\n📈 Distribuição por personalidade:")
        total_options = sum(self.personality_distribution.values())
        ideal_per_personality = total_options / len(expected_personalities)
        
        for personality in sorted(expected_personalities):
            count = self.personality_distribution.get(personality, 0)
            percentage = (count / total_options * 100) if total_options > 0 else 0
            status = "✅" if abs(count - ideal_per_personality) <= 2 else "⚠️"
            print(f"  {status} {personality:15}: {count:2d} opções ({percentage:5.1f}%)")
        
        print(f"\n📊 Total de opções: {total_options}")
        print(f"📊 Ideal por personalidade: {ideal_per_personality:.1f}")
        
        return {
            'missing': missing_personalities,
            'extra': extra_personalities,
            'distribution': dict(self.personality_distribution),
            'total_options': total_options,
            'ideal_per_personality': ideal_per_personality
        }
    
    def analyze_question_balance(self):
        """Analisa o balanceamento das perguntas"""
        print("\n⚖️  ANÁLISE DO BALANCEAMENTO DAS PERGUNTAS")
        print("=" * 60)
        
        problems = []
        
        for question in self.questions:
            personalities_in_question = [opt['personality'] for opt in question['options']]
            unique_personalities = set(personalities_in_question)
            
            analysis = {
                'id': question['id'],
                'question': question['question'][:50] + '...' if len(question['question']) > 50 else question['question'],
                'total_options': len(question['options']),
                'unique_personalities': len(unique_personalities),
                'personalities': list(unique_personalities),
                'duplicates': len(personalities_in_question) - len(unique_personalities)
            }
            
            # Verifica problemas
            if analysis['total_options'] != 4:
                problems.append(f"Pergunta {question['id']}: {analysis['total_options']} opções (esperado: 4)")
            
            if analysis['duplicates'] > 0:
                problems.append(f"Pergunta {question['id']}: Personalidades duplicadas")
            
            if analysis['unique_personalities'] < 3:
                problems.append(f"Pergunta {question['id']}: Apenas {analysis['unique_personalities']} personalidades diferentes")
            
            self.question_analysis.append(analysis)
        
        # Mostra problemas encontrados
        if problems:
            print("❌ Problemas encontrados:")
            for problem in problems:
                print(f"  • {problem}")
        else:
            print("✅ Todas as perguntas estão bem balanceadas")
        
        # Estatísticas gerais
        avg_options = sum(q['total_options'] for q in self.question_analysis) / len(self.question_analysis)
        avg_unique = sum(q['unique_personalities'] for q in self.question_analysis) / len(self.question_analysis)
        
        print(f"\n📊 Estatísticas:")
        print(f"  • Média de opções por pergunta: {avg_options:.1f}")
        print(f"  • Média de personalidades únicas por pergunta: {avg_unique:.1f}")
        
        return {
            'problems': problems,
            'avg_options': avg_options,
            'avg_unique_personalities': avg_unique,
            'question_details': self.question_analysis
        }
    
    def simulate_quiz_results(self, num_simulations=1000):
        """Simula resultados do quiz para verificar se todos os perfis são alcançáveis"""
        print("\n🎲 SIMULAÇÃO DE RESULTADOS DO QUIZ")
        print("=" * 60)
        
        import random
        
        results_counter = Counter()
        reachable_personalities = set()
        
        for _ in range(num_simulations):
            # Simula respostas aleatórias
            answers = {}
            for question in self.questions:
                if question['options']:
                    chosen_option = random.choice(question['options'])
                    answers[question['id']] = chosen_option['personality']
            
            # Calcula resultado (mesmo algoritmo do quiz)
            scores = Counter(answers.values())
            if scores:
                max_score = max(scores.values())
                winners = [p for p, score in scores.items() if score == max_score]
                result_personality = winners[0]  # Pega o primeiro em caso de empate
                
                results_counter[result_personality] += 1
                reachable_personalities.add(result_personality)
        
        print(f"🎲 Simulações executadas: {num_simulations}")
        print(f"✅ Personalidades alcançáveis: {len(reachable_personalities)}/15")
        
        if len(reachable_personalities) < 15:
            missing = self.personalities - reachable_personalities
            print(f"❌ Personalidades não alcançadas: {missing}")
        
        print("\n📊 Frequência dos resultados:")
        for personality in sorted(self.personalities):
            count = results_counter.get(personality, 0)
            percentage = (count / num_simulations * 100)
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {personality:15}: {count:4d} ({percentage:5.1f}%)")
        
        return {
            'reachable_count': len(reachable_personalities),
            'reachable_personalities': reachable_personalities,
            'missing_personalities': self.personalities - reachable_personalities,
            'results_distribution': dict(results_counter)
        }
    
    def generate_targeted_tests(self):
        """Gera testes direcionados para cada personalidade"""
        print("\n🎯 TESTES DIRECIONADOS POR PERSONALIDADE")
        print("=" * 60)
        
        successful_personalities = set()
        failed_personalities = set()
        
        for target_personality in sorted(self.personalities):
            # Cria respostas focadas nesta personalidade
            answers = {}
            for question in self.questions:
                # Procura opção da personalidade alvo
                target_option = None
                for option in question['options']:
                    if option['personality'] == target_personality:
                        target_option = option
                        break
                
                if target_option:
                    answers[question['id']] = target_personality
                else:
                    # Se não há opção para esta personalidade, escolhe a primeira
                    if question['options']:
                        answers[question['id']] = question['options'][0]['personality']
            
            # Calcula resultado
            scores = Counter(answers.values())
            if scores:
                max_score = max(scores.values())
                winners = [p for p, score in scores.items() if score == max_score]
                result_personality = winners[0]
                
                if result_personality == target_personality:
                    successful_personalities.add(target_personality)
                    print(f"  ✅ {target_personality:15}: Alcançável (score: {scores[target_personality]})")
                else:
                    failed_personalities.add(target_personality)
                    print(f"  ❌ {target_personality:15}: Falhou -> {result_personality} (score: {scores.get(target_personality, 0)})")
        
        print(f"\n📊 Resumo dos testes direcionados:")
        print(f"  ✅ Personalidades alcançáveis: {len(successful_personalities)}/15")
        print(f"  ❌ Personalidades problemáticas: {len(failed_personalities)}/15")
        
        return {
            'successful': successful_personalities,
            'failed': failed_personalities
        }
    
    def generate_report(self):
        """Gera relatório completo da análise"""
        print("\n📋 RELATÓRIO COMPLETO DE VALIDAÇÃO")
        print("=" * 60)
        
        # Executa todas as análises
        distribution_analysis = self.analyze_personality_distribution()
        balance_analysis = self.analyze_question_balance()
        simulation_results = self.simulate_quiz_results()
        targeted_tests = self.generate_targeted_tests()
        
        # Calcula score geral
        total_score = 0
        max_score = 100
        
        # Pontuação por critério
        if not distribution_analysis['missing'] and not distribution_analysis['extra']:
            total_score += 20
        
        if not balance_analysis['problems']:
            total_score += 20
        
        if simulation_results['reachable_count'] >= 13:  # Pelo menos 13/15
            total_score += 20
        elif simulation_results['reachable_count'] >= 10:
            total_score += 15
        elif simulation_results['reachable_count'] >= 7:
            total_score += 10
        
        if len(targeted_tests['successful']) >= 13:
            total_score += 20
        elif len(targeted_tests['successful']) >= 10:
            total_score += 15
        elif len(targeted_tests['successful']) >= 7:
            total_score += 10
        
        # Pontuação por balanceamento
        distribution_variance = max(distribution_analysis['distribution'].values()) - min(distribution_analysis['distribution'].values())
        if distribution_variance <= 2:
            total_score += 20
        elif distribution_variance <= 4:
            total_score += 15
        elif distribution_variance <= 6:
            total_score += 10
        
        print(f"\n🏆 SCORE FINAL: {total_score}/{max_score}")
        
        if total_score >= 90:
            print("🟢 EXCELENTE: Quiz muito bem balanceado!")
        elif total_score >= 70:
            print("🟡 BOM: Quiz funcional com pequenos ajustes necessários")
        elif total_score >= 50:
            print("🟠 REGULAR: Quiz precisa de melhorias significativas")
        else:
            print("🔴 PROBLEMÁTICO: Quiz precisa de revisão completa")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        
        if distribution_analysis['missing']:
            print(f"  • Adicionar opções para: {distribution_analysis['missing']}")
        
        if balance_analysis['problems']:
            print(f"  • Corrigir {len(balance_analysis['problems'])} problemas de balanceamento")
        
        if simulation_results['reachable_count'] < 15:
            print(f"  • Melhorar alcançabilidade de {15 - simulation_results['reachable_count']} personalidades")
        
        if len(targeted_tests['failed']) > 0:
            print(f"  • Revisar distribuição para: {targeted_tests['failed']}")
        
        return {
            'score': total_score,
            'max_score': max_score,
            'distribution': distribution_analysis,
            'balance': balance_analysis,
            'simulation': simulation_results,
            'targeted': targeted_tests
        }

def main():
    """Função principal"""
    quiz_file = "quiz-consuelo/quiz.html"
    
    print("🔍 ANALISADOR DO QUIZ DE PERSONALIDADE")
    print("=" * 60)
    print(f"📁 Analisando arquivo: {quiz_file}")
    
    analyzer = QuizAnalyzer(quiz_file)
    
    if analyzer.load_quiz():
        report = analyzer.generate_report()
        
        # Salva relatório em JSON
        report_file = "quiz_validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Relatório salvo em: {report_file}")
    else:
        print("❌ Falha ao carregar o quiz")

if __name__ == "__main__":
    main()