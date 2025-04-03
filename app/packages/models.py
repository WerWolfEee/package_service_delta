from typing import Optional
from sqlalchemy import String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, int_pk



class PackageType(Base):
    __tablename__ = 'package_types'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    packages: Mapped[list["Package"]] = relationship("Package", back_populates="package_type")
    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class Package(Base):
    __tablename__ = 'packages'

    id: Mapped[int_pk]
    title: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    weight: Mapped[int] = mapped_column(nullable=False)
    package_type_id: Mapped[int] = mapped_column(ForeignKey("package_types.id"), nullable=False)
    cost_of_contents: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), nullable=False)
    package_type: Mapped[PackageType] = relationship("PackageType", back_populates="packages")
    price: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(15, 2), nullable=True, default=None)
    user_session_id: Mapped[str] = mapped_column(String(100), nullable=False)

    extend_existing = True
