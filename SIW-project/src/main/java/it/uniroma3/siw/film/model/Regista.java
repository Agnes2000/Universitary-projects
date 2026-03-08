package it.uniroma3.siw.film.model;

import static javax.persistence.CascadeType.ALL;
import static javax.persistence.GenerationType.AUTO;

import java.time.LocalDate;
import java.util.LinkedList;
import java.util.List;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.OneToMany;
import javax.persistence.Transient;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Past;
import javax.validation.constraints.PastOrPresent;
import javax.validation.constraints.Size;

import lombok.Getter;
import lombok.Setter;
import lombok.Singular;

@Entity
@Getter @Setter
public class Regista {

    @Id
    @GeneratedValue(strategy = AUTO)
    private Long id;

    @NotBlank
    @Size(min = 1, max = 20)
    private String nome;

    @NotBlank
    @Size(min = 1, max = 20)
    private String cognome;

    @Past
    @NotNull
    private LocalDate dataDiNascita;

    @PastOrPresent
    private LocalDate dataDiMorte;

    @Singular
    @OneToMany(mappedBy = "regista", cascade = ALL)
    private List<Film> film;

    private String urlImg;

    public Regista() {
        this.film = new LinkedList<>();
    }

    @Transient
    public String getPhotosImagePath() {
        if (this.urlImg == null || this.id == null)
            return null; 
        return "/registi-img/" + this.urlImg;
    }
    
}
