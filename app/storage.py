from abc import ABC, abstractmethod


class Storage(ABC):

    # ---------- Save ----------

    @abstractmethod
    def save_snapshot(self, portfolio): ...

    @abstractmethod
    def save_positions(self, portfolio): ...

    @abstractmethod
    def save_news(self, news): ...

    @abstractmethod
    def save_earnings(self, earnings): ...

    @abstractmethod
    def save_report(self, report): ...

    # ---------- Read ----------

    @abstractmethod
    def latest_snapshot(self): ...

    @abstractmethod
    def latest_positions(self): ...

    @abstractmethod
    def today_news(self): ...

    @abstractmethod
    def latest_report(self): ...

    @abstractmethod
    def get_history(self, days): ...

    @abstractmethod
    def get_position_history(self, ticker): ...

    @abstractmethod
    def monthly_returns(self): ...