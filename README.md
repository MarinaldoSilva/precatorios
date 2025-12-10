# API de gestão de Precatórios

## Projeto

Projeto desenvolvido de forma autônoma, usando como base a documentação do Django Rest Framework e muita pesquisa. O projeto em si consiste em uma API de Marketplace de Precatórios. Para o desenvolvimento, usei os princípios S.O.L.I.D., mas tomei cuidado para não ser verboso; a simplicidade foi meu foco para ser funcional, esse foi o objetivo. Com esse sistema é possível que um usuário se cadastre com a única rota liberada para acesso sem precisar de validação de usuário/senha e Token, definindo seu perfil (Credor, Investidor ou Analista). Após isso, o user tem opções específicas baseadas em seu perfil (RBAC):

1. **Credores:** Cadastram precatórios e aceitam/recusam propostas.
2. **Analistas:** Validam e aprovam precatórios pendentes em lote.
3. **Investidores:** Visualizam oportunidades aprovadas e realizam ofertas de compra.

Para que isso seja possível, foram criadas funções e validações de acordo com as regras de negócio do mercado financeiro.

## Processo de criação

Esse foi o projeto com uma lógica simples ao mesmo tempo complexa que tem como o core central a validação de regras de negócio dentro de uma service,
a consistência de dados nas Views e o uso de Camada de Serviço (Service Layer).
Optei pelo controle e flexibilidade usando APIView combinada com ViewSets.
O usuário é injetado pela view ou service quando a requisição é feita na request, garantindo a autoria das ações.

O processo envolve verificar o tipo de usuário para conceder permissões (RBAC), validar se o valor da oferta
é menor que o valor de face, e controlar o ciclo de vida do ativo: Pendente, Disponível e Vendido.
Isso é feito quando o `serializer.is_valid()` é chamado ou dentro da lógica de serviços.
Após isso, temos a manipulação em massa no banco de dados do status com o uso de `update` em QuerySets
para aprovações em massa (Bulk Update) e `transaction.atomic` para garantir que ou seja tudo executado ou nada.

### Ativos (Precatórios)

- Cadastro de precatórios pelo Credor sempre o `status inicial` sera 'Pendente'.
- O Credor vê os seus precatórios cadastrados, Analista vê tudo, Investidor vê apenas 'Disponível' para compra
- O Analista tem o poder de trocar o status dos precatórios listados para venda.

### Aprovação e Propostas

- Aprovação em massa com o `bulk` realizada por Analistas
- Oferta não pode superar o Valor de Face do ativo
- Trava de status: Propostas só podem ser feitas em precatórios com status 'Disponível'

### Usuários e Permissões

- Cadastro de novos usuários com perfis definidos:
  - 1: Credor
  - 2: Investidor
  - 3: Analista
- Login com uso de Token JWT
- Controle de acesso com base em cargos (RBAC) nas Views.

## Endpoints

Sendo extremamente honesto, não foi fácil fazer isso, envolveu muito estudo e dedicação, agora eu vejo como ficou e penso "na teoria é simples, na prática a gente sofre", mas a vida é assim, com o passar do tempo vamos fazer isso de forma natural. Vamos listar os principais endpoints da API.

### Criar user (Sign Up)

Na rota:
`http://127.0.0.1:8000/api/v1/auth/register/`

Informamos nossas credenciais e o tipo de usuário
1: Credor
2: Investidor
3: Analista

```json
{
  "username": "investidor_01",
  "email": "investidor@mail.com",
  "password": "admin@2025",
  "first_name": "João",
  "last_name": "Silva",
  "tipo_usuario": 2
}
```

### Login

Passamos o Email e senha para ser gerado os tokens de acesso

Rota:

```http
http://127.0.0.1:8000/api/v1/auth/login/
```

```json
{
  "email": "credor@mail.com",
  "password": "minha_senha"
}
```

Tokens de acesso:

```json
{
  "id": "f90cd1c0-4359-49fe-85bc-ab2a76ee7c28",
  "username": "credor",
  "email": "credor@mail.com",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY1NDcwOTE0LCJpYXQiOjE3NjUzODQ1MTQsImp0aSI6Ijc5YzU4MjQ0NjE1YzQzZDFhMmM3ODEwNTZmMjZiNjllIiwidXNlcl9pZCI6ImY5MGNkMWMwLTQzNTktNDlmZS04NWJjLWFiMmE3NmVlN2MyOCJ9.X07bVtG8NQSj7j5ihq_bDjEfTwOQ2Ax_1-04kelVYyI",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2NjA3NTcxNCwiaWF0IjoxNzY1Mzg0NTE0LCJqdGkiOiJiZjNiZjViY2ZjYjQ0YTIxYWRmNmExNDc0NjllN2FlYSIsInVzZXJfaWQiOiJmOTBjZDFjMC00MzU5LTQ5ZmUtODViYy1hYjJhNzZlZTdjMjgifQ.m8U1DpR6jEGeRAdQiJbnjPttL9-YWviCatX8qaW_Gi8"
}
```

### Criar precatórios

Rota:

```http
http://127.0.0.1:8000/api/v1/ativos/precatorio/
```

```json
{
  "titulo": "titulo_precatorio",
  "valor_face": 100000.0,
  "valor_inicial": 730000.0,
  "tribunal": "TRF-5 CIDADE-BR",
  "status": 1
}
```

Retorno:

```json
{
"id": "4034cab7-c07c-44d2-b988-7da384436964",
"dono": { ... },
"titulo": "Precatório TJSP 2025",
"valor_face": "100000.00",
"status": 1
}
```

### Listagem de precatórios

Rota:

```http
http://127.0.0.1:8000/api/v1/ativos/precatorio/
```

Retorno do json

```json
[
  {
    "id": "46114081-8496-4c09-9969-14518f992c27",
    "dono": {
      "id": "f90cd1c0-4359-49fe-85bc-ab2a76ee7c28",
      "last_login": null,
      "is_superuser": false,
      "username": "credor",
      "first_name": "",
      "last_name": "",
      "is_staff": false,
      "is_active": true,
      "date_joined": "2025-12-10T16:31:08.469649Z",
      "tipo_usuario": 1,
      "email": "credor@mail.com",
      "groups": [],
      "user_permissions": []
    },
    "titulo": "Petrobras",
    "valor_face": "100000.00",
    "valor_inicial": "730000.00",
    "tribunal": "TRF-5 RECIFE",
    "status": 1
  },
  {
    "id": "093e5719-bbf0-4754-bef2-6212660a9647",
    "dono": {
      "id": "f90cd1c0-4359-49fe-85bc-ab2a76ee7c28",
      "last_login": null,
      "is_superuser": false,
      "username": "credor",
      "first_name": "",
      "last_name": "",
      "is_staff": false,
      "is_active": true,
      "date_joined": "2025-12-10T16:31:08.469649Z",
      "tipo_usuario": 1,
      "email": "credor@mail.com",
      "groups": [],
      "user_permissions": []
    },
    "titulo": "caixa",
    "valor_face": "100000.00",
    "valor_inicial": "730000.00",
    "tribunal": "TRF-5 RECIFE",
    "status": 1
  }
]
```

### Aprovação em Massa somente por analistas

Rota:

```http
http://127.0.0.1:8000/api/v1/ativos/precatorio/aprovacao/bulk/
```

```json
{
  "ids": [
    "46114081-8496-4c09-9969-14518f992c27",
    "093e5719-bbf0-4754-bef2-6212660a9647",
    "95118d4c-1e7c-4e65-a2be-fbfcdbab43b3",
    "46114081-8496-4c09-9969-14518f992c27",
    "244e78ab-9978-43a0-994e-bb745577208c"
  ]
}
```

Podemos passar somente 1 UUID porém dentro de um formato de lista.

Retorno:

```json
{
  "result": "Foram aprovados: 4 precatórios"
}
```

### Proposta de compra de pprecatórios

Rota:

```http
http://127.0.0.1:8000/api/v1/ativos/precatorio/proposta/
```

```json
{
  "precatorio": "46114081-8496-4c09-9969-14518f992c27",
  "valor_oferta": 73000.0
}
```

Retorno

```json
{
  "id": "9c5d7308-d0e1-43eb-9f86-0c6c140d0a18",
  "precatorio": "46114081-8496-4c09-9969-14518f992c27",
  "valor_oferta": "73000.00",
  "data_criacao": "2025-12-10T16:36:14.529059Z",
  "status": 1
}
```

### Retorno de proposta de intenção

```http
http://127.0.0.1:8000/api/v1/ativos/precatorio/gerenciar/propostas/
```

```json
{
  "proposta_id": "9c5d7308-d0e1-43eb-9f86-0c6c140d0a18",
  "acao": "ACEITAR"
}
```

Retorno da solicitação:

```json
{
  "result": "venda do precatorio realizada com sucesso."
}
```

### Documentação

A documentação foi gerada com o Swagger, assim a visualização dos dados será mais amigável.

Na rota:

```http
http://127.0.0.1:8000/api/docs/
```

Ao acessar o link com o repositório já baixado é possível ver toda a documentação do projeto.

O banco é criado de forma automática quando executamos as migrations e migrate do projeto.
