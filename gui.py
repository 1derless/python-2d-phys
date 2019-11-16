import tkinter
import tkinter.messagebox


from colliding_world import Material


__all__ = ['get_material']


class MaterialSelectWindow:
    def __init__(self):
        self.material = None
        self.tk = tkinter.Tk()
        self.tk.resizable(False, False)
        self.tk.title('Edit Material')

        self.restitution = AttributeSet(
            self.tk,
            row=0,
            name='Coefficient of restitution',
            hint='Coefficient of restitution: the amount of kinetic '
                 'energy conserved in every collision.',
            error_msg='Coefficient of restitution must be a number '
                      'greater than or equal to zero.',
            validity_check=lambda x: is_float(x) and float(x) >= 0,
        )

        self.density = AttributeSet(
            self.tk,
            row=1,
            name='Density',
            hint='Density: the amount of mass per unit volume.',
            error_msg='Density must be a number greater than zero.',
            validity_check=lambda x: is_float(x) and float(x) > 0,
        )

        self.static_friction = AttributeSet(
            self.tk,
            row=2,
            name='Coefficient of Static Friction',
            hint='Coefficient of Static Friction: the coefficient of '
                 'friction of two objects stationary in relation to '
                 'each other.',
            error_msg='Coefficient of static friction must be a number '
                      'greater than or equal to zero.',
            validity_check=lambda x: is_float(x) and float(x) >= 0,
        )

        self.dynamic_friction = AttributeSet(
            self.tk,
            row=3,
            name='Coefficient of Dynamic Friction',
            hint='Coefficient of Dynamic Friction: the coefficient of '
                 'friction between two moving objects of this material.',
            error_msg='Coefficient of dynamic friction must be a number'
                      ' greater than or equal to zero.',
            validity_check=lambda x: is_float(x) and float(x) >= 0,
        )

        self.ok_button = tkinter.Button(
            text='OK',
            command=self.ok_clicked,
        )
        self.ok_button.grid(row=4, columnspan=3)

    def ok_clicked(self):
        errors = []
        if not self.restitution.is_valid():
            errors.append(self.restitution.error_msg)
        if not self.density.is_valid():
            errors.append(self.density.error_msg)
        if not self.static_friction.is_valid():
            errors.append(self.static_friction.error_msg)
        if not self.dynamic_friction.is_valid():
            errors.append(self.dynamic_friction.error_msg)

        if errors:
            tkinter.messagebox.showerror('Bad Input', '\n'.join(errors))
        else:
            self.material = Material(
                restitution=float(self.restitution.get()),
                dynamic_friction=float(self.dynamic_friction.get()),
                static_friction=float(self.static_friction.get()),
                density=float(self.density.get()),
            )

            self.tk.destroy()

    def run(self):
        self.tk.mainloop()

        # When the tk is destroyed,
        return self.material


class AttributeSet:
    def __init__(self, master, row, name, hint, error_msg, validity_check):
        self.validity_check = validity_check
        self.error_msg = error_msg

        self.label = tkinter.Label(master, text=name)
        self.label.grid(row=row, column=0)

        self.entry = tkinter.Entry(master)
        self.entry.grid(row=row, column=1)

        self.info_button = tkinter.Button(
            master,
            text='i',
            fg='blue',
            underline=0,
            command=lambda: tkinter.messagebox.showinfo(
                name + ' information',
                hint,
            )
        )
        self.info_button.grid(row=row, column=2)

    def get(self):
        return self.entry.get()

    def is_valid(self):
        return self.validity_check(self.entry.get())


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_material():
    m = MaterialSelectWindow()
    return m.run()


if __name__ == '__main__':
    print(get_material())
