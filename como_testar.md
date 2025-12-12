Esse documento foi gerado por IA pra testar a aplicação.

## 1. Criar os Usuários (Sign Up)

Vamos criar os 3 perfis necessários para o teste.

**Rota:** `POST http://127.0.0.1:8000/api/v1/auth/register/`

### 1.1 Criar Credor

**Payload:**

```json
{
  "username": "credor_teste",
  "email": "credor@teste.com",
  "password": "senha_secreta",
  "first_name": "Sr.",
  "last_name": "Credor",
  "tipo_usuario": 1
}


1.2 Criar Investidor
Payload:

JSON

{
  "username": "investidor_teste",
  "email": "investidor@teste.com",
  "password": "senha_secreta",
  "first_name": "Sra.",
  "last_name": "Investidora",
  "tipo_usuario": 2
}
1.3 Criar Analista (Quem aprova)
Payload:

JSON

{
  "username": "analista_teste",
  "email": "analista@teste.com",
  "password": "senha_secreta",
  "first_name": "Dr.",
  "last_name": "Analista",
  "tipo_usuario": 3
}
2. Obter Tokens (Login)
Você precisará alternar entre os usuários para realizar as ações. Faça login com cada um e guarde os tokens.

Rota: POST http://127.0.0.1:8000/api/v1/auth/login/

Login Credor: credor@teste.com / senha_secreta -> Copie o Token (TOKEN_CREDOR).

Login Investidor: investidor@teste.com / senha_secreta -> Copie o Token (TOKEN_INVESTIDOR).

Login Analista: analista@teste.com / senha_secreta -> Copie o Token (TOKEN_ANALISTA).

3. Cadastrar Precatório (Ação do Credor)
O credor coloca o ativo na plataforma.

Rota: POST http://127.0.0.1:8000/api/v1/ativos/precatorio/

Auth: Bearer TOKEN_CREDOR

Payload:

JSON

{
  "titulo": "Precatório Federal Teste 2025",
  "valor_face": 100000.00,
  "valor_inicial": 85000.00,
  "tribunal": "TRF-1"
}
Resultado Esperado: 201 Created.

⚠️ Importante: Copie o ID (UUID) do precatório gerado na resposta (ex: 4034cab7-c07c...). Vamos chamar de UUID_PRECATORIO.

4. Aprovar Precatório (Ação do Analista)
O precatório nasceu com status "Pendente". O investidor não consegue comprar ainda. O analista precisa liberar.

Rota: PATCH http://127.0.0.1:8000/api/v1/ativos/precatorio/aprovacao-bulk/

Auth: Bearer TOKEN_ANALISTA

Payload:

JSON

{
  "ids": ["UUID DO PRECATÓRIO"]
}
Resultado Esperado: 200 OK. Mensagem: "Foram aprovados: 1 precatórios".

5. Fazer Proposta (Ação do Investidor)
Agora que está com status "Disponível", o investidor faz uma oferta.

Rota: POST http://127.0.0.1:8000/api/v1/ativos/precatorio/aprovacao/

Auth: Bearer TOKEN_INVESTIDOR

Payload:

JSON

{
  "precatorio": "COLE_O_UUID_PRECATORIO_AQUI",
  "valor_oferta": 90000.00
}
Resultado Esperado: 201 Created.

⚠️ Importante: Copie o ID (UUID) da PROPOSTA gerada na resposta. Vamos chamar de UUID_PROPOSTA.

6. Aceitar Proposta e Vender (Ação do Credor)
O credor aceita a oferta, o que vende o ativo e finaliza o processo.

Rota: POST http://127.0.0.1:8000/api/v1/ativos/precatorio/gerenciar-proposta/

Auth: Bearer TOKEN_CREDOR

Payload:

JSON

{
  "proposta_id": "COLE_O_UUID_PROPOSTA_AQUI",
  "acao": "ACEITAR"
}
Resultado Esperado: 200 OK. Mensagem: "Venda do precatório realizada com sucesso."
```
