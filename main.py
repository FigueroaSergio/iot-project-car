from models.car import Car


def main():
    car = Car(velocity=2, acceleration=10)

    print(car.model_dump())


if __name__ == "__main__":
    main()
