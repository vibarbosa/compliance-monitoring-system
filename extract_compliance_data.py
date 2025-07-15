import requests
import pandas as pd
import random
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('compliance_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Simula integração de API interna
class ComplianceAPI:
    
    def __init__(self, api_key: str, base_url: str = "https://api.mercadolibre.com/compliance_alerts?status=open&limit=100"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_alert_ids(self, days_back: int = 30) -> List[str]:
        endpoint = f"{self.base_url}"
        params = {
            'start_date': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
            'status': 'active',
            'limit': 1000
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            return [alert['id'] for alert in response.json()['data']]
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            raise

# Simula uma chamada get de API publica     
    def get_public_data(alert_id: int = None) -> Dict[str, Any]:
       
        base_url = "https://api.mercadolibre.com/compliance_alerts"
        
        # filtro por alert_id
        if alert_id:
            url = f"{base_url}/{alert_id}"
        else:
            url = f"{base_url}"
        
        try:
            logger.info(f"Iniciando requisição GET para: {url}")
            
            response = requests.get(
                url,
                timeout=10
            )
            
            response.raise_for_status()
            
            logger.info("Requisição realizada com sucesso!")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            raise

# Gera dados para simulação de extração
class FakeInternalAPI:
    
    @staticmethod
    def get_alert_ids(count: int = 100) -> List[str]:
        return [f"ALERT-{str(i).zfill(5)}" for i in range(1, count+1)]

class FakePublicAPI:
    
    @staticmethod
    def get_alert_details(alert_id: str) -> Dict[str, Any]:
        
        alert_types = [
                "Fatura Duplicada",
                "Fornecedor Não Aprovado",
                "Valor Inconsistente",
                "Data de Emissão Inválida",
                "Taxa Calculada Incorretamente",
                "Nota Fiscal Inexistente",
                "Alteração Não Autorizada",
                "Classificação Fiscal Incorreta"
            ]
        
        statuses = [
                "Aberto",
                "Em Análise",
                "Pendente Aprovação",
                "Resolvido",
                "Fechado",
                "Reaberto",
                "Escalado para Fiscal"
            ]
        
        impacts = [
            "Baixo",
            "Moderado",
            "Alto",
            "Crítico"
        ]
        
        creation_date = datetime.now() - timedelta(days=random.randint(1, 90))
        status = random.choice(statuses)
        
        # Gera resolution_date apenas para status Resolvido ou Fechado
        if status in ["Resolvido", "Fechado"]:
            resolution_date = creation_date + timedelta(days=random.randint(1, 30))
        else:
            resolution_date = None
        
        return {
            "alert_id": alert_id,
            "type_of_alert": random.choice(alert_types),
            "status": status,
            "assigned_to": f"usuario{random.randint(1, 20)}@mercadolivre.com",
            "creation_date": creation_date.strftime("%Y-%m-%d"),
            "resolution_date": resolution_date.strftime("%Y-%m-%d") if resolution_date else None,
            "impact_level": random.choice(impacts),
            "description": f"Descrição teste - {alert_id}",
            "source": random.choice(["Fornecedor A", "Fornecedor B", "Fornecedor C"]),
            "priority": random.randint(1, 5)
        }

# Classe principal
class ComplianceMonitor:
    
    def __init__(self):
        self.internal_api = FakeInternalAPI()
        self.public_api = FakePublicAPI()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.current_date = datetime.now().strftime("%Y%m%d")
        self.output_dir = self.create_output_directory()

# Cria diretório de saída com base na data atual        
    def create_output_directory(self) -> str:
        dir_name = f"Compliance {self.current_date}"
        output_dir = os.path.join(self.script_dir, dir_name)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Diretório criado: {output_dir}")
        
        return output_dir

# Gera nome do arquivo de acordo com data e hora
    def get_output_filename(self, base_name: str = "compliance_alerts") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.csv"

# Grava caminho do diretório  
    def get_output_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)

# Inicia a extração dos dados de alertas
    def fetch_alerts(self, alert_count: int = 100) -> List[Dict[str, Any]]:
        logging.info(f"Iniciando extração de {alert_count} alertas...")
        
        try:
            alert_ids = self.internal_api.get_alert_ids(alert_count)
            alerts = []
            
            for i, alert_id in enumerate(alert_ids, 1):
                try:
                    alerts.append(self.public_api.get_alert_details(alert_id))
                    if i % 10 == 0:
                        logging.info(f"Progresso: {i}/{alert_count} alertas processados")
                except Exception as e:
                    logging.error(f"Erro ao processar alerta {alert_id}: {str(e)}")
                    continue
            
            logging.info(f"Extração concluída. {len(alerts)} alertas obtidos com sucesso.")
            return alerts
        
        except Exception as e:
            logging.error(f"Falha na extração de alertas: {str(e)}")
            raise

# Extrai contagens relevantes para analise
    def generate_analysis_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        analysis_data = []
        
        # Contagem por tipo de alerta
        for typ, count in df['type_of_alert'].value_counts().items():
            analysis_data.append({
                "Categoria": "Tipo de Alerta",
                "Item": typ,
                "Quantidade": count,
                "Percentual": f"{count/len(df)*100:.1f}%"
            })
        
        # Contagem por status
        for status, count in df['status'].value_counts().items():
            analysis_data.append({
                "Categoria": "Status",
                "Item": status,
                "Quantidade": count,
                "Percentual": f"{count/len(df)*100:.1f}%"
            })
        
        # Contagem por nível de impacto
        for impact, count in df['impact_level'].value_counts().items():
            analysis_data.append({
                "Categoria": "Nível de Impacto",
                "Item": impact,
                "Quantidade": count,
                "Percentual": f"{count/len(df)*100:.1f}%"
            })
             
        return pd.DataFrame(analysis_data)

# Gera arquivos CSV
    def process_alerts_to_csv(self, alerts: List[Dict[str, Any]], base_filename: str = "compliance_alerts") -> tuple:

        data_filename = f"{base_filename}_dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        analysis_filename = f"{base_filename}_analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        data_path = self.get_output_path(data_filename)
        analysis_path = self.get_output_path(analysis_filename)
        
        try:
            df = pd.DataFrame(alerts)
            selected_fields = [
                'alert_id', 'type_of_alert', 'status', 'assigned_to',
                'creation_date', 'resolution_date', 'impact_level',
                'priority', 'source', 'description'
            ]
            
            df[selected_fields].to_csv(
                data_path, 
                index=False,
                encoding='utf-8-sig',
                sep=';',
                quotechar='"'
            )
            
            df_analysis = self.generate_analysis_csv(df)
            df_analysis.to_csv(
                analysis_path,
                index=False,
                encoding='utf-8-sig',
                sep=';',
                quotechar='"'
            )
            
            logger.info(f"Dados salvos com sucesso em: {data_path}")
            logger.info(f"Análise exploratória salva em: {analysis_path}")
            
            return data_path, analysis_path
            
        except Exception as e:
            logger.error(f"Erro ao processar alertas: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        monitor = ComplianceMonitor()
        alerts = monitor.fetch_alerts(100)
        
        # Agora retorna dois paths: dados e análise
        data_path, analysis_path = monitor.process_alerts_to_csv(alerts)
        
        logging.info(f"Processo concluído com sucesso!")
        logging.info(f"Dados originais: {data_path}")
        logging.info(f"Análise exploratória: {analysis_path}")
        
    except Exception as e:
        logging.error(f"Erro no processo principal: {str(e)}")
        exit(1)