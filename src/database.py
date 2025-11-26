from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import pandas as pd
from src.config import config
from src.logger import logger

Base = declarative_base()

class Portfolio(Base):
    __tablename__ = 'portfolio'
    
    symbol = Column(String, primary_key=True)
    shares = Column(Float, default=0.0)
    avg_price = Column(Float, default=0.0)
    value = Column(Float, default=0.0)
    last_buy_date = Column(Date, nullable=True)
    last_sell_date = Column(Date, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=date.today)
    symbol = Column(String, nullable=False)
    action = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    cash_after = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        if not config.DATABASE_URL:
            logger.warning("DATABASE_URL not set. Database features disabled.")
            self.engine = None
            self.Session = None
            return

        try:
            self.engine = create_engine(config.DATABASE_URL)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to database.")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.engine = None
            self.Session = None

    def get_session(self):
        if self.Session:
            return self.Session()
        return None

    def load_portfolio(self):
        """Load portfolio from DB as DataFrame."""
        if not self.engine:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql(self.Session().query(Portfolio).statement, self.Session().bind)
            # Ensure columns match expected format
            if df.empty:
                 return pd.DataFrame(columns=["symbol", "shares", "avg_price", "value",
                                  "last_buy_date", "last_sell_date"])
            
            # Convert date columns to string isoformat to match CSV behavior if needed, 
            # but keeping as date objects is better. 
            # For compatibility with existing code which expects strings in some places, 
            # we might need adjustment. Let's see.
            return df
        except Exception as e:
            logger.error(f"Error loading portfolio from DB: {e}")
            return pd.DataFrame()

    def save_portfolio(self, pf: pd.DataFrame):
        """Save portfolio DataFrame to DB."""
        if not self.engine:
            return
        
        session = self.get_session()
        try:
            # Upsert logic is complex with pandas to_sql, so we'll do row by row for safety/simplicity
            # or delete all and rewrite (simple but risky if crash).
            # Given it's a small portfolio (500 max), delete and rewrite is acceptable for now.
            
            session.query(Portfolio).delete()
            
            records = pf.to_dict('records')
            for record in records:
                # Handle date conversion if they are strings
                if isinstance(record.get('last_buy_date'), str):
                    record['last_buy_date'] = datetime.strptime(record['last_buy_date'], '%Y-%m-%d').date()
                if isinstance(record.get('last_sell_date'), str) and record.get('last_sell_date'):
                    record['last_sell_date'] = datetime.strptime(record['last_sell_date'], '%Y-%m-%d').date()
                elif record.get('last_sell_date') == "":
                    record['last_sell_date'] = None
                    
                p = Portfolio(**{k: v for k, v in record.items() if k in Portfolio.__table__.columns.keys()})
                session.add(p)
            
            session.commit()
            logger.info("Portfolio saved to DB.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving portfolio to DB: {e}")
        finally:
            session.close()

    def record_trade(self, symbol, action, qty, price, cash):
        """Record a trade to DB."""
        if not self.engine:
            return
            
        session = self.get_session()
        try:
            trade = Trade(
                symbol=symbol,
                action=action,
                quantity=qty,
                price=price,
                cash_after=cash
            )
            session.add(trade)
            session.commit()
            logger.info(f"Trade recorded in DB: {action} {symbol}")
        except Exception as e:
            logger.error(f"Error recording trade to DB: {e}")
        finally:
            session.close()

db = Database()
