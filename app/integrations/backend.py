import asyncio
import httpx
from app.config import get_settings

settings=get_settings()

class BackendError(Exception): pass

class BackendClient:
    def __init__(self):
        self.base=settings.backend_base_url.rstrip("/")
        self.timeout=settings.backend_timeout_seconds

    async def request(self, method, path, *, token=None, **kwargs):
        headers={"Accept":"application/json","Content-Type":"application/json"}
        if settings.backend_service_token:
            headers["X-Service-Token"]=settings.backend_service_token
        if token:
            headers["Authorization"]=f"Bearer {token}"
        last=None
        for attempt in range(settings.backend_max_retries+1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as c:
                    r=await c.request(method,self.base+path,headers=headers,**kwargs)
                if r.status_code in (408,429) or r.status_code >= 500:
                    last=BackendError(f"temporary backend error {r.status_code}")
                    if attempt < settings.backend_max_retries:
                        await asyncio.sleep(0.5*(2**attempt))
                        continue
                if r.status_code >= 400:
                    raise BackendError(f"backend {r.status_code}: {r.text[:500]}")
                return r.json() if r.content else None
            except (httpx.TimeoutException,httpx.NetworkError) as e:
                last=e
                if attempt < settings.backend_max_retries:
                    await asyncio.sleep(0.5*(2**attempt))
                    continue
        raise BackendError(str(last))

    # Identity
    async def request_link_code(self, telegram_user_id):
        return await self.request("POST","/api/v1/integrations/telegram/link-code",json={"telegram_user_id":telegram_user_id})
    async def confirm_link_code(self, code, telegram_user_id):
        return await self.request("POST","/api/v1/integrations/telegram/confirm-link",json={"code":code,"telegram_user_id":telegram_user_id})

    # Seller
    async def products(self,t): return await self.request("GET","/api/v1/me/products",token=t)
    async def product(self,t,pid): return await self.request("GET",f"/api/v1/me/products/{pid}",token=t)
    async def create_product(self,t,data): return await self.request("POST","/api/v1/me/products",token=t,json=data)
    async def update_product(self,t,pid,data): return await self.request("PATCH",f"/api/v1/me/products/{pid}",token=t,json=data)
    async def delete_product(self,t,pid): return await self.request("DELETE",f"/api/v1/me/products/{pid}",token=t)

    # Orders/Cargo
    async def orders(self,t): return await self.request("GET","/api/v1/me/orders",token=t)
    async def order(self,t,oid): return await self.request("GET",f"/api/v1/me/orders/{oid}",token=t)

    # Wallet
    async def wallet(self,t): return await self.request("GET","/api/v1/me/wallet",token=t)
    async def wallet_operations(self,t): return await self.request("GET","/api/v1/me/wallet/operations",token=t)
    async def top_up(self,t,amount): return await self.request("POST","/api/v1/me/wallet/top-up",token=t,json={"amount":amount})
    async def withdraw(self,t,amount): return await self.request("POST","/api/v1/me/wallet/withdraw",token=t,json={"amount":amount})

    # Team
    async def team(self,t,level=None,status=None,query=None):
        params={k:v for k,v in {"level":level,"status":status,"q":query}.items() if v is not None}
        return await self.request("GET","/api/v1/me/team",token=t,params=params)

    # Status/subscription
    async def status(self,t): return await self.request("GET","/api/v1/me/status",token=t)
    async def subscription(self,t): return await self.request("GET","/api/v1/me/subscription",token=t)
    async def subscription_payments(self,t): return await self.request("GET","/api/v1/me/subscription/payments",token=t)
    async def subscription_pay(self,t,plan_id): return await self.request("POST","/api/v1/me/subscription/pay",token=t,json={"plan_id":plan_id})

    # Cooperation
    async def cooperation_create(self,t,data): return await self.request("POST","/api/v1/cooperation-applications",token=t,json=data)
    async def cooperation_list(self,t): return await self.request("GET","/api/v1/me/cooperation-applications",token=t)

    # Backend events can be acknowledged/queried through the main backend if needed.
    async def integration_event_ack(self,event_id): return await self.request("POST","/api/v1/integrations/telegram/events/ack",json={"event_id":event_id})
